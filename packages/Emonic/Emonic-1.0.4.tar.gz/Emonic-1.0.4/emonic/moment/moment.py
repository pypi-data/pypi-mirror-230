from datetime import datetime, timedelta
from markupsafe import Markup

class Moment:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.template_env.globals['moment'] = self.inject_moment_js
        app.context_processor(self.inject_moment_js)

    def format_datetime(self):
        def format_datetime(dt, format_string='YYYY-MM-DD HH:mm:ss'):
            # Implement your formatting logic using moment.js
            return f'<script>document.write(moment("{dt.isoformat()}").format("{format_string}"));</script>'

        return {'format_datetime': format_datetime}

    def inject_moment_js(self):
        return {'moment': 'https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.1/moment.min.js'}

    def relative_time(self, date):
        return Markup(f'<script>document.write(moment("{date}").fromNow());</script>')

    def calendar_time(self, date):
        return Markup(f'<script>document.write(moment("{date}").calendar());</script>')

    def duration(self, duration_seconds):
        return Markup(f'<script>document.write(moment.duration({duration_seconds}, "seconds").humanize());</script>')

    def unix_timestamp(self, date):
        return Markup(f'<script>document.write(moment("{date}").unix());</script>')

    def format_from_now(self, date, suppress_prefix=False):
        prefix = '' if suppress_prefix else 'in '
        return Markup(f'<script>document.write(moment("{date}").fromNow({{"withoutSuffix": suppress_prefix}}));</script>')

    def format_diff(self, start_date, end_date, precision='seconds', suppress_suffix=False):
        suffix = '' if suppress_suffix else True
        return Markup(f'<script>document.write(moment("{end_date}").diff("{start_date}", "{precision}", {{"withoutSuffix": suppress_suffix}}));</script>')


    def format_timezone(self, date, timezone='UTC'):
        return Markup(f'<script>document.write(moment("{date}").tz("{timezone}").format());</script>')

    def add_duration(self, date, duration_seconds, unit='seconds'):
        return Markup(f'<script>document.write(moment("{date}").add({duration_seconds}, "{unit}").format());</script>')

    def subtract_duration(self, date, duration_seconds, unit='seconds'):
        return Markup(f'<script>document.write(moment("{date}").subtract({duration_seconds}, "{unit}").format());</script>')

    def start_of(self, date, unit='day'):
        return Markup(f'<script>document.write(moment("{date}").startOf("{unit}").format());</script>')

    def end_of(self, date, unit='day'):
        return Markup(f'<script>document.write(moment("{date}").endOf("{unit}").format());</script>')

    def is_after(self, date1, date2):
        return Markup(f'<script>document.write(moment("{date1}").isAfter("{date2}"));</script>')

    def is_before(self, date1, date2):
        return Markup(f'<script>document.write(moment("{date1}").isBefore("{date2}"));</script>')

    def is_same_or_before(self, date1, date2):
        return Markup(f'<script>document.write(moment("{date1}").isSameOrBefore("{date2}"));</script>')

    def is_same_or_after(self, date1, date2):
        return Markup(f'<script>document.write(moment("{date1}").isSameOrAfter("{date2}"));</script>')

    def is_between(self, date, range_start, range_end, inclusive=False):
        inclusive_str = '[]' if inclusive else '()'
        return Markup(f'<script>document.write(moment("{date}").isBetween("{range_start}", "{range_end}", "{inclusive_str}"));</script>')

    def is_leap_year(self, date):
        return Markup(f'<script>document.write(moment("{date}").isLeapYear());</script>')

    def days_in_month(self, date):
        return Markup(f'<script>document.write(moment("{date}").daysInMonth());</script>')

    def humanize(self, date):
        return Markup(f'<script>document.write(moment("{date}").humanize());</script>')

    def week_number(self, date):
        return Markup(f'<script>document.write(moment("{date}").week("{date}"));</script>')

    def utc_datetime(self, date):
        return Markup(f'<script>document.write(moment.utc("{date}").format());</script>')

    def local_datetime(self, date, timezone='UTC'):
        return Markup(f'<script>document.write(moment("{date}").tz("{timezone}").format());</script>')

    def first_day_of_week(self, date, weekday=0):
        return Markup(f'<script>document.write(moment("{date}").day("{weekday}").startOf("week").format());</script>')

    def last_day_of_week(self, date, weekday=6):
        return Markup(f'<script>document.write(moment("{date}").day("{weekday}").endOf("week").format());</script>')

    def add_years(self, date, years):
        return Markup(f'<script>document.write(moment("{date}").add({years}, "years").format());</script>')

    def add_months(self, date, months):
        return Markup(f'<script>document.write(moment("{date}").add({months}, "months").format());</script>')

    def add_weeks(self, date, weeks):
        return Markup(f'<script>document.write(moment("{date}").add({weeks}, "weeks").format());</script>')

    def add_days(self, date, days):
        return Markup(f'<script>document.write(moment("{date}").add({days}, "days").format());</script>')

    def add_hours(self, date, hours):
        return Markup(f'<script>document.write(moment("{date}").add({hours}, "hours").format());</script>')

    def add_minutes(self, date, minutes):
        return Markup(f'<script>document.write(moment("{date}").add({minutes}, "minutes").format());</script>')

    def add_seconds(self, date, seconds):
        return Markup(f'<script>document.write(moment("{date}").add({seconds}, "seconds").format());</script>')

    def subtract_years(self, date, years):
        return Markup(f'<script>document.write(moment("{date}").subtract({years}, "years").format());</script>')

    def subtract_months(self, date, months):
        return Markup(f'<script>document.write(moment("{date}").subtract({months}, "months").format());</script>')

    def subtract_weeks(self, date, weeks):
        return Markup(f'<script>document.write(moment("{date}").subtract({weeks}, "weeks").format());</script>')

    def subtract_days(self, date, days):
        return Markup(f'<script>document.write(moment("{date}").subtract({days}, "days").format());</script>')

    def subtract_hours(self, date, hours):
        return Markup(f'<script>document.write(moment("{date}").subtract({hours}, "hours").format());</script>')

    def subtract_minutes(self, date, minutes):
        return Markup(f'<script>document.write(moment("{date}").subtract({minutes}, "minutes").format());</script>')

    def subtract_seconds(self, date, seconds):
        return Markup(f'<script>document.write(moment("{date}").subtract({seconds}, "seconds").format());</script>')
