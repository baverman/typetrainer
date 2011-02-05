from typetrainer.stat import FileStatistic
from datetime import datetime, timedelta

def test_stat_must_collect_and_get(tmpdir):
    stat = FileStatistic(str(tmpdir.join()))

    dt = datetime.now()
    stat.log('name', 150, 100, dt)

    result = stat.get('name', 100)
    assert result == {dt.date():(150, 1)}

def test_stat_result_must_not_contain_records_with_low_accuracies(tmpdir):
    stat = FileStatistic(str(tmpdir.join()))

    dt = datetime.now()
    stat.log('name', 150, 100, dt)
    stat.log('name', 140, 99, dt)

    result = stat.get('name', 100)
    assert result == {dt.date():(150, 1)}

def test_stat_must_return_records_averaged_by_day(tmpdir):
    stat = FileStatistic(str(tmpdir.join()))

    dt1 = datetime.now()
    dt2 = dt1 + timedelta(days=1)

    stat.log('name', 150, 100, dt1)
    stat.log('name', 140, 100, dt1)
    stat.log('name', 100, 100, dt2)
    stat.log('name', 120, 100, dt2)

    result = stat.get('name', 100)
    assert result == {dt1.date():(145, 2), dt2.date():(110, 2)}
