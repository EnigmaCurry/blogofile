def browserbot(driver, function, *args):
    """Selenium Javascript Helpers"""
    # Original copyright and license for browserbot.js (http://is.gd/Bz4xPc):
    # Copyright (c) 2009-2011 Jari Bakken

    # Permission is hereby granted, free of charge, to any person obtaining
    # a copy of this software and associated documentation files (the
    # "Software", to) deal in the Software without restriction, including
    # without limitation the rights to use, copy, modify, merge, publish,
    # distribute, sublicense, and/or sell copies of the Software, and to
    # permit persons to whom the Software is furnished to do so, subject to
    # the following conditions:

    # The above copyright notice and this permission notice shall be
    # included in all copies or substantial portions of the Software.

    # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    # EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    # MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    # NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
    # LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
    # OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
    # WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
    browserbot_js = """var browserbot = {

        getOuterHTML: function(element) {
            if (element.outerHTML) {
                return element.outerHTML;
            } else if (typeof(XMLSerializer) != undefined) {
                return new XMLSerializer().serializeToString(element);
            } else {
                throw "can't get outerHTML in this browser";
            }
        }

    };
    """
    js = browserbot_js + \
        "return browserbot.{0}.apply(browserbot, arguments);".format(function)
    return driver.execute_script(js,*args)

def html(web_element):
    """Return the HTML for a Selenium WebElement"""
    return browserbot(web_element.parent, "getOuterHTML", web_element)
