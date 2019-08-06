from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from hashlib import md5
from flask import url_for, render_template
from app import db, login


class StatusTypes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(128), unique=True)
    password_hash = db.Column(db.String(128))
    # is_verified = db.Column(db.Boolean, default=False)
    sign_up_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    # verification_timestamp = db.Column(db.DateTime)
    current_status_id = db.Column(db.Integer, db.ForeignKey('status_types.id'))
    filters = db.relationship('Filter', lazy='dynamic')
    comments = db.relationship('Comment', backref=db.backref('user'), lazy='dynamic')
    notes = db.relationship('Note',
                            backref=db.backref('user'),
                            order_by="desc(Note.creation_timestamp)",
                            lazy='dynamic')

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def get_friends(self, status='accepted'):
        friends = Friends.query.filter(db.or_(Friends.origin_user == self.id, Friends.other_user == self.id))
        if status != 'all':
            friends = friends.filter_by(status=status)

        user_ids = [x.other_user if x.origin_user == self.id else x.origin_user for x in friends.all()]
        return User.query.filter(User.id.in_(user_ids)).all()

    def get_friends_others(self, status='accepted'):
        friends = Friends.query.filter(Friends.origin_user == self.id)
        if status != 'all':
            friends = friends.filter_by(status=status)

        user_ids = [x.other_user for x in friends.all()]
        return User.query.filter(User.id.in_(user_ids)).all()

    def get_friends_origins(self, status='accepted'):
        friends = Friends.query.filter(Friends.other_user == self.id)
        if status != 'all':
            friends = friends.filter_by(status=status)

        user_ids = [x.origin_user for x in friends.all()]
        return User.query.filter(User.id.in_(user_ids)).all()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def unfriend_friend(self, user):
        friendship = Friends.query.filter(db.or_(db.and_(Friends.other_user == user.id,
                                                         Friends.origin_user == self.id),
                                                 db.and_(Friends.origin_user == user.id,
                                                         Friends.other_user == self.id))).first()
        db.session.delete(friendship)
        db.session.commit()

    def send_friend_request(self, user):
        existing_relationships = self.get_friends(status='all')
        if user not in existing_relationships and user.id != self.id:
            new_friend_request = Friends(origin_user=self.id, other_user=user.id)
            db.session.add(new_friend_request)
            db.session.commit()

    def respond_friend_request(self, user, response='accepted'):
        pending_request = Friends.query.filter_by(origin_user=user.id, other_user=self.id, status='pending').first()
        if pending_request:
            pending_request.status = response if response == 'accepted' or response == 'blocked' else 'accepted'
            pending_request.request_response_timestamp = datetime.utcnow()
            db.session.commit()

    def get_most_recent_location(self):
        return UserLocationTracking.query.filter_by(user_id=self.id).order_by(
            UserLocationTracking.timestamp.desc()).first()

    def update_location(self, latitude, longitude):
        UserLocationTracking(user_id=self.id, latitude=latitude, longitude=longitude)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)


@login.user_loader
def load_user(uid):
    return User.query.get(int(uid))


class Friends(db.Model):
    origin_user = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    other_user = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    status = db.Column(db.String(10), default='pending')
    request_sent_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    request_response_timestamp = db.Column(db.DateTime)

    def __init__(self, *args, **kwargs):
        super(Friends, self).__init__(*args, **kwargs)


class UserLocationTracking(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, primary_key=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    user = db.relationship('User', backref=db.backref('location_history',
                                                      order_by="desc(UserLocationTracking.timestamp)",
                                                      lazy='dynamic'))

    def __init__(self, *args, **kwargs):
        super(UserLocationTracking, self).__init__(*args, **kwargs)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))

    def __init__(self, *args, **kwargs):
        super(Tag, self).__init__(*args, **kwargs)


class Region(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    radius = db.Column(db.Float)

    notes = db.relationship('Note', backref=db.backref('region'))

    def __init__(self, *args, **kwargs):
        super(Region, self).__init__(*args, **kwargs)


class RecurrencePattern(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recurrence_type = db.Column(db.String(10))
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    separation_count = db.Column(db.SmallInteger)
    day_of_week = db.Column(db.SmallInteger)
    week_of_month = db.Column(db.SmallInteger)
    day_of_month = db.Column(db.SmallInteger)
    month_of_year = db.Column(db.SmallInteger)

    def __init__(self, *args, **kwargs):
        super(RecurrencePattern, self).__init__(*args, **kwargs)


UserFilterTags = db.Table(
    'user_filter_tags',
    db.Column('filter_id', db.Integer, db.ForeignKey('filter.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)

UserFilterTime = db.Table(
    'user_filter_time',
    db.Column('filter_id', db.Integer, db.ForeignKey('filter.id')),
    db.Column('recurrence_id', db.Integer, db.ForeignKey('recurrence_pattern.id'))
)

UserFilterLocation = db.Table(
    'user_filter_location',
    db.Column('filter_id', db.Integer, db.ForeignKey('filter.id')),
    db.Column('region_id', db.Integer, db.ForeignKey('region.id'))
)


class Filter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('status_types.id'))
    tags = db.relationship('Tag',
                           secondary=UserFilterTags,
                           backref=db.backref('filters', lazy='dynamic'),
                           lazy='dynamic')
    regions = db.relationship('Region',
                              secondary=UserFilterLocation,
                              backref=db.backref('filters', lazy='dynamic'),
                              lazy='dynamic')
    recurrences = db.relationship('RecurrencePattern',
                                  secondary=UserFilterTime,
                                  backref=db.backref('filters', lazy='dynamic'),
                                  lazy='dynamic')

    def __init__(self, *args, **kwargs):
        super(Filter, self).__init__(*args, **kwargs)


NoteTags = db.Table(
    'note_tags',
    db.Column('note_id', db.Integer, db.ForeignKey('note.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)

NoteVisibility = db.Table(
    'note_visibility',
    db.Column('note_id', db.Integer, db.ForeignKey('note.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

NotePatterns = db.Table(
    'note_patterns',
    db.Column('note_id', db.Integer, db.ForeignKey('note.id')),
    db.Column('recurrence_id', db.Integer, db.ForeignKey('recurrence_pattern.id'))
)


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(150))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    creation_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))
    is_public = db.Column(db.Boolean)
    is_recurring = db.Column(db.Boolean)
    is_shared_with_friends = db.Column(db.Boolean)
    is_commentable = db.Column(db.Boolean)

    tags = db.relationship('Tag',
                           secondary=NoteTags,
                           backref=db.backref('notes', lazy='dynamic'),
                           lazy='dynamic')

    pattern = db.relationship('RecurrencePattern',
                              secondary=NotePatterns,
                              backref=db.backref('notes', lazy='dynamic'),
                              lazy='dynamic')

    visibility = db.relationship('User',
                                 secondary=NoteVisibility,
                                 backref=db.backref('visible_notes', lazy='dynamic'),
                                 lazy='dynamic')

    comments = db.relationship('Comment', lazy='dynamic')

    def __init__(self, *args, **kwargs):
        super(Note, self).__init__(*args, **kwargs)

    def format_comments(self):
        def make_struct(comment_obj, level):
            replies = []
            if comment_obj.replies:
                for each_comment in comment_obj.replies:
                    replies.append(make_struct(each_comment, level + 1))
            return render_template('comment.html',
                                   username_url=url_for('user', username=comment_obj.user.username),
                                   username=comment_obj.user.username,
                                   comment_content=comment_obj.content,
                                   comment_id=comment_obj.id,
                                   repliles="".join(replies))

        chains = []
        for each_top_comment in self.comments.filter_by(parent=None):
            chains.append(make_struct(each_top_comment, 1))

        return "".join(chains)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    parent_comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    content = db.Column(db.String(150))
    replies = db.relationship('Comment',
                              backref=db.backref('parent', remote_side=[id]),
                              lazy='dynamic')

    def __init__(self, *args, **kwargs):
        super(Comment, self).__init__(*args, **kwargs)
