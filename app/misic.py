from math import acos, cos, sin, radians
from datetime import datetime
from app import db
from app.models import User, Filter, Note, RecurrencePattern as RP


def calc_distance(latitude1, longitude1, latitude2, longitude2, measurement='km'):
    measurements = {'mi': 3961, 'km': 6373, 'm': 6373000, 'ft': 20914080}
    return acos(
        cos(radians(latitude1)) *
        cos(radians(latitude2)) *
        cos(radians(longitude2) - radians(longitude1)) +
        sin(radians(latitude1)) * sin(radians(latitude2))
    ) * measurements[measurement]


def in_range(latitude1, longitude1, latitude2, longitude2, radius):
    return calc_distance(latitude1, longitude1, latitude2, longitude2) <= radius


def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month


def check_rp(recurrence):
    current_datetime = datetime.now()
    basic_check = False

    if (recurrence.start_time <= current_datetime.time() <= recurrence.end_time and
            recurrence.start_date <= current_datetime.date() <= recurrence.end_date):
        basic_check = True

    if not recurrence.recurrence_type:
        return basic_check

    if recurrence.recurrence_type == 'daily':
        return ((current_datetime.date() - recurrence.start_date).days % recurrence.separation_count) == 0
    elif recurrence.recurrence_type == 'weekly':
        return (((current_datetime.date() - recurrence.start_date).days // 7) % recurrence.separation_count) == 0
    elif recurrence.recurrence_type == 'monthly':
        return diff_month(current_datetime.date(), recurrence.start_date) % recurrence.separation_count == 0
    else:
        return (current_datetime.date().year - recurrence.start_date.year) % recurrence.separation_count == 0


def get_visible_nodes(user):
    current_datetime = datetime.now()
    user_location = user.get_most_recent_location()
    if not user_location:
        return []

    user_filter = Filter.query.filter_by(user_id=user.id, status_id=user.current_status_id).first()

    if not user_filter:
        note_rps = set()
        note_rps_dist = set()

        all_patterns = RP.query.filter(db.and_(RP.start_time <= current_datetime.time(),
                                               RP.end_time >= current_datetime.time(),
                                               RP.start_date <= current_datetime.date(),
                                               RP.end_date >= current_datetime.date()))
        no_patterns = all_patterns.filter_by(recurrence_type=None)
        no_patterns = [rp for rp in no_patterns if check_rp(rp)]
        daily_patterns = all_patterns.filter_by(recurrence_type='daily')
        daily_patterns = [rp for rp in daily_patterns if check_rp(rp)]
        weekly_patterns = all_patterns.filter_by(recurrence_type='weekly',
                                                 day_of_week=current_datetime.isoweekday())
        weekly_patterns = [rp for rp in weekly_patterns if check_rp(rp)]
        monthly_patterns = all_patterns.filter_by(recurrence_type='monthly',
                                                  day_of_week=current_datetime.isoweekday()).all()
        monthly_patterns = [rp for rp in monthly_patterns if check_rp(rp)]
        yearly_patterns = all_patterns.filter_by(recurrence_type='yearly',
                                                 day_of_week=current_datetime.isoweekday(),
                                                 month_of_year=current_datetime.month).all()
        yearly_patterns = [rp for rp in yearly_patterns if check_rp(rp)]

        for each_pattern in no_patterns + daily_patterns + weekly_patterns + monthly_patterns + yearly_patterns:
            note_rps.add(each_pattern.notes.first())

        for each_note in note_rps:
            if each_note:
                if in_range(each_note.region.latitude, each_note.region.longitude,
                            user_location.latitude, user_location.longitude, each_note.region.radius):
                    note_rps_dist.add(each_note)

        return list(note_rps_dist)

    else:

        user_filter_notes = {}
        user_filter_tags = user_filter.tags.all()
        user_filter_regions = user_filter.regions.all()
        user_filter_recurrences = user_filter.recurrences.all()
        all_notes = Note.query.all()

        if user_filter_tags:
            user_filter_notes['tags'] = []
            for each_tag in user_filter_tags:
                user_filter_notes['tags'].extend(each_tag.notes.all())
            user_filter_notes['tags'] = set(user_filter_notes['tags'])

        if user_filter_regions:
            user_filter_notes['regions'] = set()
            for each_region in user_filter_regions:
                for each_note in all_notes:
                    if in_range(each_note.region.latitude, each_note.region.longitude,
                                each_region.latitude, each_region.longitude, each_region.radius):
                        user_filter_notes['regions'].add(each_note)

        if user_filter_recurrences:
            user_filter_notes['recurrences'] = set()
            for each_note in all_notes:
                for each_rp in user_filter_recurrences:
                    temp1 = check_rp(each_rp)
                    temp2 = check_rp(each_note.pattern.first())
                    if temp1 and temp2:
                        user_filter_notes['recurrences'].add(each_note)

        valid_notes = []
        for each_note in set.intersection(*user_filter_notes.values()):
            if in_range(each_note.region.latitude, each_note.region.longitude,
                        user_location.latitude, user_location.longitude, each_note.region.radius):
                valid_notes.append(each_note)

        return valid_notes


if __name__ == '__main__':
    u1 = User.query.filter_by(username='rjones218').first()
    print(get_visible_nodes(u1))
