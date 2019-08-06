from datetime import datetime

from flask import flash, redirect, request, render_template, url_for, abort
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, RegistrationForm, CreateNoteForm, CreateFilterForm, CommentForm, UserTrackingForm, StatusTypesForm
from app.models import StatusTypes, User, UserLocationTracking, Tag, \
    Region, RecurrencePattern, Filter, Note, Comment
from app.misic import get_visible_nodes

default_status = StatusTypes.query.filter_by(name='no status').first()


@app.route('/')
@app.route('/index')
@login_required
def index():
    visible_notes = sorted([note for note in get_visible_nodes(current_user) if
                            note.is_public or current_user in note.visibility],
                           key=lambda x: x.creation_timestamp, reverse=True)

    return render_template('index.html', notes=visible_notes)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.lower()).first()

        if user is None or not user.check_password(form.password.data):
            flash('failure$Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')

        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')

        return redirect(next_page)

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(username=form.username.data.lower(),
                    first_name=form.first_name.data.lower(),
                    last_name=form.last_name.data.lower(),
                    email=form.email.data.lower(),
                    current_status_id=default_status.id)

        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('success$You are now a registered user !')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/user/<username>/password/reset/<newpassword>')
def super_secret_password_admin_tool(username, newpassword):
    local_user = User.query.filter_by(username=username).first_or_404()
    local_user.set_password(newpassword)
    db.session.commit()
    flash('failure$you are a hacker !!!')
    return redirect('index')


@app.route('/user/<username>')
@login_required
def user(username):
    local_user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=local_user)


@app.route('/user/<username>/tracking', methods=['GET', 'POST'])
def user_tracking(username):
    local_user = User.query.filter_by(username=username).first_or_404()
    form = UserTrackingForm()

    if form.validate_on_submit():
        if not form.time.data or not form.date.data:
            local_timestamp = datetime.utcnow()
        else:
            local_timestamp = datetime.combine(form.date.data, form.time.data)
        tracker = UserLocationTracking(user_id=local_user.id,
                                       timestamp=local_timestamp,
                                       latitude=form.latitude.data,
                                       longitude=form.longitude.data)
        db.session.add(tracker)
        db.session.commit()
        flash('info$Updated location of user {} !'.format(username))
        return redirect(url_for('user_tracking', username=username))

    return render_template('tracking.html', user=local_user, form=form, notes=Note.query.all())


@app.route('/filters')
@login_required
def filters():
    local_filters = current_user.filters.all()
    return render_template('filters.html', filters=local_filters)


@app.route('/filters/active')
@login_required
def active_filters():
    local_filters = current_user.filters.filter_by(status_id=current_user.current_status_id).all()
    return render_template('filters.html', filters=local_filters)


@app.route('/filters/inactive')
@login_required
def inactive_filters():
    local_filters = current_user.filters.filter(Filter.status_id != current_user.current_status_id).all()
    return render_template('filters.html', filters=local_filters)


@app.route('/friends/send_request/<username>')
@login_required
def send_friend_request(username):
    local_user = User.query.filter_by(username=username).first_or_404()
    current_user.send_friend_request(local_user)
    flash('info$Sent friend request')
    return redirect(url_for('user', username=username))


@app.route('/friends/accept/<username>')
@login_required
def accept_friend_request(username):
    local_user = User.query.filter_by(username=username).first_or_404()
    current_user.respond_friend_request(local_user, response='accepted')
    flash('success$You and {} are now friends'.format(username))
    return redirect(url_for('user', username=username))


@app.route('/friends/block/<username>')
@login_required
def block_friend_request(username):
    local_user = User.query.filter_by(username=username).first_or_404()
    current_user.respond_friend_request(local_user, response='blocked')
    flash('failure$You blocked {}'.format(username))
    return redirect(url_for('user', username=username))


@app.route('/friends/delete/<username>')
@login_required
def delete_friend(username):
    local_user = User.query.filter_by(username=username).first_or_404()
    current_user.unfriend_friend(local_user)
    flash('failure$You un-friended {}'.format(username))
    return redirect(url_for('user', username=username))


@app.route('/note/<note_id>', methods=['GET', 'POST'])
@login_required
def note(note_id):
    local_note = Note.query.get_or_404(note_id)
    if not local_note.is_public and current_user not in local_note.visibility:
        return abort(404)

    form = CommentForm()

    if form.validate_on_submit():
        parent_id = form.parent_id.data
        new_comment = Comment(note_id=note_id,
                              user_id=current_user.id,
                              content=form.content.data,
                              parent_comment_id=parent_id if parent_id else None)
        db.session.add(new_comment)
        db.session.commit()
        flash('success$Comment posted !')

        return redirect(url_for('note', note_id=note_id))
    return render_template('note.html', note=local_note, form=form)


@app.route('/note/<note_id>/comment/<comment_id>')
@login_required
def comment_on_comment(note_id, comment_id):
    local_note = Note.query.get_or_404(note_id)
    parent_comment = Comment.query.get_or_404(comment_id)
    form = CommentForm()

    if form.validate_on_submit():
        new_comment = Comment(note_id=note_id, user_id=current_user.id, content=form.content.data)
        parent_comment.replies.append(new_comment)
        db.session.commit()
        flash('success$Comment posted !')

        return redirect(url_for('note', note_id=note_id))
    return render_template('note.html', note=local_note, form=form)


@app.route('/note/new', methods=['GET', 'POST'])
@login_required
def new_note():
    form = CreateNoteForm()
    if form.validate_on_submit():
        local_note = Note(content=form.content.data,
                          created_by=current_user.id,
                          is_public=not form.is_private.data,
                          is_recurring=form.is_recurring.data,
                          is_shared_with_friends=form.is_shared_with_friends.data,
                          is_commentable=form.is_commentable.data)
        db.session.add(local_note)

        # Create tags-----------------------
        raw_tags = form.tags.data.split('$')
        clean_tags = [tag.lower() for tag in [tag.strip() for tag in raw_tags] if ' ' not in tag and tag]
        tags = []

        for each_clean_tag in clean_tags:
            temp_tag = Tag.query.filter_by(name=each_clean_tag).first()

            if not temp_tag:
                temp_tag = Tag(name=each_clean_tag)
                db.session.add(temp_tag)

            tags.append(temp_tag)

        # Create region-------------------------
        if form.region_name.data:
            local_region = Region.query.filter_by(name=form.region_name.data).first()
        else:
            local_region = Region(latitude=form.latitude.data,
                                  longitude=form.longitude.data,
                                  radius=form.radius.data)
            db.session.add(local_region)

        # Create Recurrence Pattern----------------
        recurrence = RecurrencePattern(recurrence_type=form.recurrence_type.data if form.recurrence_type.data else None,
                                       start_time=form.start_time.data,
                                       end_time=form.end_time.data,
                                       start_date=form.start_date.data,
                                       end_date=form.end_date.data,
                                       separation_count=form.separation_count.data if form.separation_count.data > 0 else None,
                                       day_of_week=form.day_of_week.data if form.day_of_week.data else None,
                                       week_of_month=form.week_of_month.data if form.week_of_month.data else None,
                                       day_of_month=form.day_of_month.data if form.day_of_month.data else None,
                                       month_of_year=form.month_of_year.data if form.month_of_year.data else None)
        db.session.add(recurrence)
        db.session.flush()

        # Adjust note visibility
        local_note.region_id = local_region.id
        if not local_note.is_public:
            local_note.visibility.append(current_user)
            if local_note.is_shared_with_friends:
                local_note.visibility.extend(current_user.get_friends())

        local_note.tags.extend(tags)
        local_note.pattern.append(recurrence)

        db.session.commit()
        flash('success$Note has been created !')
        return redirect(url_for('note', note_id=local_note.id))

    return render_template('new_note.html', form=form)


@app.route('/tag/<tag_id>/notes')
@login_required
def find_notes_with_tag(tag_id):
    local_tag = Tag.query.get_or_404(tag_id)
    visible_notes = sorted([note for note in local_tag.notes if
                            note.is_public or current_user in note.visibility],
                           key=lambda x: x.creation_timestamp, reverse=True)

    return render_template('tags.html', tag_name=local_tag, notes=visible_notes)


@app.route('/filters/new', methods=['GET', 'POST'])
@login_required
def create_filter():
    form = CreateFilterForm()
    if form.validate_on_submit():
        local_filter = Filter.query.filter_by(user_id=current_user.id, status_id=int(form.status_name.data)).first()

        if not local_filter:
            local_filter = Filter(name=form.name.data,
                                  user_id=current_user.id,
                                  status_id=int(form.status_name.data))
            db.session.add(local_filter)
            db.session.flush()

        # Create tags-----------------------
        raw_tags = form.tags.data.split('$')
        clean_tags = [tag.lower() for tag in [tag.strip() for tag in raw_tags] if ' ' not in tag and tag]
        tags = []

        for each_clean_tag in clean_tags:
            temp_tag = Tag.query.filter_by(name=each_clean_tag).first()

            if not temp_tag:
                temp_tag = Tag(name=each_clean_tag)
                db.session.add(temp_tag)

            tags.append(temp_tag)

        # Create region-------------------------
        if form.region_name.data:
            local_region = Region.query.filter_by(name=form.region_name.data).first()
        else:
            local_region = Region(latitude=form.latitude.data,
                                  longitude=form.longitude.data,
                                  radius=form.radius.data)
            db.session.add(local_region)

        # Create Recurrence Pattern----------------
        recurrence = RecurrencePattern(
            recurrence_type=form.recurrence_type.data if form.recurrence_type.data else None,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            separation_count=form.separation_count.data if form.separation_count.data > 0 else None,
            day_of_week=form.day_of_week.data if form.day_of_week.data else None,
            week_of_month=form.week_of_month.data if form.week_of_month.data else None,
            day_of_month=form.day_of_month.data if form.day_of_month.data else None,
            month_of_year=form.month_of_year.data if form.month_of_year.data else None)
        db.session.add(recurrence)
        db.session.flush()

        local_filter.regions.append(local_region)
        local_filter.tags.extend(tags)
        local_filter.recurrences.append(recurrence)

        db.session.commit()
        flash('success$Filter has been created !')
        return redirect(url_for('index'))

    return render_template('new_filter.html', form=form)


@app.route('/status', methods=['GET', 'POST'])
@login_required
def change_status():
    form = StatusTypesForm()

    if form.validate_on_submit():
        current_user.current_status_id = int(form.status_name.data)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('status.html', form=form)


