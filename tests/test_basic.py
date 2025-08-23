from atcoder_problem_converter import AtCoderProblemParser

SAMPLE_HTML = """
<html>
<head><title>ABC001 A - 積雪深差</title></head>
<body>
<p>Time Limit: 2 sec / Memory Limit: 1024 MB</p>
<div id="task-statement">
  <span class="lang-ja">
    <section>
      <h3>問題文</h3>
      <p>2 つの観測所での積雪深がそれぞれ <var>a</var> cm, <var>b</var> cm であるとき、差を求めよ。</p>
      <h3>入力</h3>
      <p>入力は以下の形式で標準入力から与えられる。</p>
      <pre>a b</pre>
      <h3>出力</h3>
      <p>答えを出力せよ。</p>
      <h3>制約</h3>
      <ul>
        <li>0 \leq a, b \leq 100</li>
      </ul>
    </section>
  </span>
</div>
</body>
</html>
"""

def test_parse_basic():
    parser = AtCoderProblemParser(SAMPLE_HTML, language='ja')
    md = parser.parse()
    assert '# ABC001 A - 積雪深差' in md
    assert 'Time Limit' in md
    # Variables converted to LaTeX style $a$ $b$
    assert '$a$' in md and '$b$' in md
