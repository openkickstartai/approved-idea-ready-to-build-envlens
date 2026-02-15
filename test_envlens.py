"""Tests for EnvLens scanner."""
import json
import pytest
from envlens import scan_source, scan_configs, parse_dotenv, analyze, format_table


def _write(tmp_path, files):
    for name, content in files.items():
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    return str(tmp_path)


def test_scan_python_getenv(tmp_path):
    path = _write(tmp_path, {
        'app.py': 'import os\ndb = os.getenv("DATABASE_URL")\nk = os.environ["SECRET_KEY"]\n'
    })
    result = scan_source(path)
    assert 'DATABASE_URL' in result
    assert 'SECRET_KEY' in result
    assert len(result) == 2


def test_scan_node_process_env(tmp_path):
    path = _write(tmp_path, {
        'server.js': 'const port = process.env.PORT\nconst h = process.env.HOST\n'
    })
    result = scan_source(path)
    assert 'PORT' in result
    assert 'HOST' in result


def test_scan_go_getenv(tmp_path):
    path = _write(tmp_path, {
        'main.go': 'package main\nimport "os"\nfunc main() { v := os.Getenv("GO_SECRET") }\n'
    })
    result = scan_source(path)
    assert 'GO_SECRET' in result


def test_scan_java_getenv(tmp_path):
    path = _write(tmp_path, {
        'App.java': 'class App { void m() { System.getenv("JAVA_HOME"); } }\n'
    })
    result = scan_source(path)
    assert 'JAVA_HOME' in result


def test_parse_dotenv(tmp_path):
    f = tmp_path / '.env'
    f.write_text('DATABASE_URL=postgres://localhost\nSECRET_KEY=abc\n# comment\nexport REDIS_URL=redis://x\n')
    result = parse_dotenv(str(f))
    assert result == {'DATABASE_URL', 'SECRET_KEY', 'REDIS_URL'}


def test_scan_configs_dotenv(tmp_path):
    path = _write(tmp_path, {'.env': 'API_KEY=xxx\nDB_HOST=localhost\n'})
    result = scan_configs(path)
    assert 'API_KEY' in result
    assert 'DB_HOST' in result


def test_scan_configs_docker_compose(tmp_path):
    path = _write(tmp_path, {
        'docker-compose.yml': 'services:\n  app:\n    environment:\n      API_KEY: xxx\n      DB_HOST: localhost\n'
    })
    result = scan_configs(path)
    assert 'API_KEY' in result
    assert 'DB_HOST' in result


def test_scan_configs_k8s_env_list(tmp_path):
    path = _write(tmp_path, {
        'deploy.yml': 'spec:\n  containers:\n    - name: app\n      env:\n        - name: K8S_VAR\n          value: hello\n'
    })
    result = scan_configs(path)
    assert 'K8S_VAR' in result


def test_analyze_missing_vars(tmp_path):
    path = _write(tmp_path, {
        'app.py': 'import os\nos.getenv("MISSING_VAR")\nos.getenv("PRESENT_VAR")\n',
        '.env': 'PRESENT_VAR=hello\n',
    })
    r = analyze(path)
    assert 'MISSING_VAR' in r['missing']
    assert 'PRESENT_VAR' in r['matched']
    assert r['summary']['missing'] == 1
    assert r['summary']['matched'] == 1


def test_analyze_ghost_vars(tmp_path):
    path = _write(tmp_path, {
        'app.py': 'import os\nos.getenv("USED_VAR")\n',
        '.env': 'USED_VAR=1\nGHOST_VAR=2\n',
    })
    r = analyze(path)
    assert 'GHOST_VAR' in r['ghost']
    assert 'USED_VAR' in r['matched']
    assert r['summary']['ghost'] == 1


def test_format_table_output(tmp_path):
    path = _write(tmp_path, {
        'app.py': 'import os\nos.getenv("DB_URL")\n',
        '.env': 'UNUSED=1\n',
    })
    r = analyze(path)
    output = format_table(r)
    assert 'DB_URL' in output
    assert 'UNUSED' in output
    assert 'MISSING' in output
    assert 'GHOST' in output


def test_analyze_empty_project(tmp_path):
    r = analyze(str(tmp_path))
    assert r['summary']['source'] == 0
    assert r['summary']['config'] == 0
    assert r['summary']['missing'] == 0
    assert r['summary']['ghost'] == 0
    assert r['summary']['matched'] == 0


def test_skips_git_directory(tmp_path):
    path = _write(tmp_path, {
        '.git/hooks/pre-commit.sh': 'os.getenv("GIT_INTERNAL")\n',
        'app.py': 'import os\nos.getenv("REAL_VAR")\n',
    })
    r = scan_source(path)
    assert 'GIT_INTERNAL' not in r
    assert 'REAL_VAR' in r
