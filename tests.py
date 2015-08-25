import unittest
from template import process_template

class TemplateTests(unittest.TestCase):

    def check_template(self, tmpl, scope, expected_output):
        compiled_template = process_template(tmpl)
        output = compiled_template.render(scope)
        self.assertEqual(output, expected_output)

    def test_variable_interpolation(self):
        tmpl = """{{ foo }}"""
        expected_output = "wow"
        scope = {
            "foo": "wow"
        }
        self.check_template(tmpl, scope, expected_output)

    def test_variable_is_interpolated_with_surrounding_text(self):
        self.check_template("a{{foo}}c", { "foo": "b" }, "abc")

    def test_for_loop(self):
        tmpl = """
<ul>
{% for item in items %}
    <li>{{ item }}</li>
{% endfor %}
</ul>
        """
        expected_output = """
<ul>
    <li>one</li>
    <li>two</li>
    <li>three</li>
    <li>four</li>
    <li>five</li>
</ul>
        """
        items = ["one", "two", "three", "four", "five"]
        self.check_template(tmpl, { "items": items }, expected_output)

    def test_for_loop_without_newlines(self):
        tmpl = """<ul>{% for item in items %}<li>{{ item }}</li>{% endfor %}</ul>"""
        expected_output = """<ul><li>a</li><li>b</li></ul>"""
        items = ["a", "b"]
        self.check_template(tmpl, { "items": items }, expected_output)

    def test_for_loop_without_newlines(self):
        tmpl = """
<ul>{% for item in items %}<li>{{ item }}</li>
{% endfor %}
</ul>"""
        expected_output = """
<ul><li>a</li>
<li>b</li>
<li>c</li>
</ul>"""
        items = ["a", "b", "c"]
        self.check_template(tmpl, { "items": items }, expected_output)

    def test_function_call_in_variable_substitution(self):
        tmpl = """The {{ exclaim('doge') }} of Venice"""
        expected_output = "The doge! of Venice"""
        scope = {
            "exclaim": lambda x: x + "!",
        }
        self.check_template(tmpl, scope, expected_output)

if __name__ == "__main__":
    unittest.main()
