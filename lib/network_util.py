import datetime
import subprocess
import os
import urllib.request


def connection_test_ping(host, test_until):
    """
    Makes a test with ping until a time specified. This test is by minute.
    :param host: Host to ping.
    :param test_until: datetime until the test will be executed.
    :return:
    """
    
    if not isinstance(host, str):
        return None
    if not isinstance(test_until, datetime.datetime):
        return None
    if test_until <= datetime.datetime.now():
        return None
    test_until = datetime.datetime.strptime(test_until.isoformat()[:16], '%Y-%m-%dT%H:%M')
    minutes_a = []
    minutes_execs = [0]
    minutes_succeeded = [0]
    minutes_times = []
    i = 0
    now = datetime.datetime.strptime(datetime.datetime.now().isoformat()[:16], '%Y-%m-%dT%H:%M')
    started = now
    minute_tested_now = 'm_' + now.isoformat()[0:4] + now.isoformat()[5:7] + now.isoformat()[8:10] + '_' + now.isoformat()[11:13] + now.isoformat()[14:16]
    minutes_a.append(minute_tested_now)
    while now <= test_until:
        minute_tested_now = 'm_' + now.isoformat()[0:4] + now.isoformat()[5:7] + now.isoformat()[8:10] + '_' + now.isoformat()[11:13] + now.isoformat()[14:16]
        if minute_tested_now != minutes_a[-1]:
            minutes_a.append(minute_tested_now)
            minutes_execs.append(0)
            minutes_succeeded.append(0)
            i += 1
        minutes_execs[i] += 1
        ping_succeeded, ping_time = ping(host)
        if ping_succeeded:
            minutes_succeeded[i] += 1
            time_r = {
                'minute': minute_tested_now,
                'time': ping_time
            }
            minutes_times.append(time_r)
        now = datetime.datetime.strptime(datetime.datetime.now().isoformat()[:16], '%Y-%m-%dT%H:%M')
    minutes = tuple(minutes_a)
    started_i = started
    results_a = []
    while started_i <= test_until:
        minute_str = 'm_' + started_i.isoformat()[0:4] + started_i.isoformat()[5:7] + started_i.isoformat()[8:10] + '_' + started_i.isoformat()[11:13] + started_i.isoformat()[14:16]
        r = {
            'minute': minute_str,
            'succeeded_percent': 0.0,
            'execs': 0,
            'succeeded': 0,
            'times': [],
            'times_avg': 0.0
        }
        if minute_str in minutes:
            i = minutes.index(minute_str)
            r['execs'] = minutes_execs[i]
            r['succeeded'] = minutes_succeeded[i]
            if r['execs'] > 0:
                r['succeeded_percent'] = float(r['succeeded']) / float(r['execs'])
        results_a.append(r)
        started_i = started_i + datetime.timedelta(minutes=1)
    results = tuple(results_a)
    for mt in minutes_times:
        if mt['minute'] in minutes:
            i = minutes.index(mt['minute'])
            results[i]['times'].append(mt['time'])
    for i in range(len(results)):
        m = results[i]['minute']
        results[i]['minute'] = '{0}-{1}-{2}T{3}:{4}'.format(m[2:6], m[6:8], m[8:10], m[11:13], m[13:15])
        if len(results[i]['times']) > 0:
            results[i]['times_avg'] = float(sum(results[i]['times'])) / float(len(results[i]['times']))
    return results


def connection_test_url(url, test_until):
    """
    Makes a test to an URL, gives the results in minutes.
    :rtype: list
    :param url: URL to test the response.
    :param test_until: datetime until the test will be executed.
    :return:
    """
    if not isinstance(url, str):
        return None
    if not isinstance(test_until, datetime.datetime):
        return None
    if test_until <= datetime.datetime.now():
        return None
    test_until = datetime.datetime.strptime(test_until.isoformat()[:16], '%Y-%m-%dT%H:%M')
    minutes_a = []
    minutes_execs = [0]
    minutes_succeeded = [0]
    i = 0
    now = datetime.datetime.strptime(datetime.datetime.now().isoformat()[:16], '%Y-%m-%dT%H:%M')
    started = now
    minute_tested_now = 'm_' + now.isoformat()[0:4] + now.isoformat()[5:7] + now.isoformat()[8:10] + '_' + now.isoformat()[11:13] + now.isoformat()[14:16]
    minutes_a.append(minute_tested_now)
    while now <= test_until:
        minute_tested_now = 'm_' + now.isoformat()[0:4] + now.isoformat()[5:7] + now.isoformat()[8:10] + '_' + now.isoformat()[11:13] + now.isoformat()[14:16]
        if minute_tested_now != minutes_a[-1]:
            minutes_a.append(minute_tested_now)
            minutes_execs.append(0)
            minutes_succeeded.append(0)
            i += 1
        minutes_execs[i] += 1
        try:
            with urllib.request.urlopen(url) as resp:
                if resp.code == 200:
                    minutes_succeeded[i] += 1
        except:
            pass
        now = datetime.datetime.strptime(datetime.datetime.now().isoformat()[:16], '%Y-%m-%dT%H:%M')
    minutes = tuple(minutes_a)
    started_i = started
    results_a = []
    while started_i <= test_until:
        minute_str = 'm_' + started_i.isoformat()[0:4] + started_i.isoformat()[5:7] + started_i.isoformat()[8:10] + '_' + started_i.isoformat()[11:13] + started_i.isoformat()[14:16]
        r = {
            'minute': minute_str,
            'succeeded_percent': 0.0,
            'execs': 0,
            'succeeded': 0
        }
        if minute_str in minutes:
            i = minutes.index(minute_str)
            r['execs'] = minutes_execs[i]
            r['succeeded'] = minutes_succeeded[i]
            if r['execs'] > 0:
                r['succeeded_percent'] = float(r['succeeded']) / float(r['execs'])
        results_a.append(r)
        started_i = started_i + datetime.timedelta(minutes=1)
    results = tuple(results_a)
    for i in range(len(results)):
        m = results[i]['minute']
        results[i]['minute'] = '{0}-{1}-{2}T{3}:{4}'.format(m[2:6], m[6:8], m[8:10], m[11:13], m[13:15])
    return results


def response_from_url_ok(url):
    resp_ok = False
    try:
        with urllib.request.urlopen(url) as req_res:
            if req_res.code == 200:
                resp_ok = True
    except:
        pass
    return resp_ok


def ping(host):
    """
    Makes a ping to a host.
    :param host: The host to ping.
    :return: (succeeded, time)
    """
    succeeded = False
    time = 0.0
    if isinstance(host, str):
        if os.name == 'posix':
            ping_sub = subprocess.Popen(
                ['ping', '-c', '1', host],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            out, error = ping_sub.communicate()
            out_str = str(out, 'ascii')
            out_lines = out_str.split('\n')
            if len(out_lines) > 1:
                if out_lines[1].find('64 bytes') != -1 and out_lines[1].find('time=') != -1:
                    succeeded = True
                    time = float(out_lines[1].split('time=')[1].split(' ')[0])
        elif os.name == 'nt':
            pass
    return succeeded, time

if __name__ == '__main__':
    print('URL test')
    test_result = connection_test_url('http://primosoft.com.mx', datetime.datetime(2016, 3, 15, 11, 30))
    for r in test_result:
        print(r['minute'])
        print('  Execs: {0}'.format(r['execs']))
        print('  Succeeded: {0}'.format(r['succeeded']))
        print('  Succeeded Percent: {0}%'.format(r['succeeded_percent'] * 100.0))
    # end for
# end if
