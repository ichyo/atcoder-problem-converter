from unittest.mock import patch, Mock
from pathlib import Path

from atcoder_problem_converter.main import convert_url

SAMPLE_HTML = """
<html>
<head><title>ABC419 E - Sample Title</title></head>
<body>
<p>Time Limit: 3 sec / Memory Limit: 1024 MB</p>
<div id="task-statement">
  <span class="lang-en">
    <section>
      <h3>Problem Statement</h3>
      <p>Example with variable <var>x_1</var>.</p>
    </section>
  </span>
</div>
</body>
</html>
"""

def test_convert_url_basic(tmp_path: Path):
  m = Mock()
  m.status_code = 200
  m.text = SAMPLE_HTML
  # requests is imported inside convert_url, so we patch the top-level 'requests.get'
  with patch('requests.get', return_value=m) as get_mock:
    out_file = tmp_path / 'output.md'
    convert_url('https://atcoder.jp/contests/abc419/tasks/abc419_e', str(out_file), language='en')
    assert out_file.exists()
    content = out_file.read_text(encoding='utf-8')
    assert '# ABC419 E - Sample Title' in content
    assert '$x_{1}$' in content  # variable formatting
    get_mock.assert_called_once()
