from pprint import pformat
import nose.tools
nose_eq = nose.tools.eq_

def eq_(actual, desired, msg=''):
    compare = 'actual:\n%s\n\n' 'desired:\n%s' % (
        pformat(actual), pformat(desired))
    mymsg = '%s\n%s' % (msg, compare)
    nose_eq(actual, desired, mymsg)
