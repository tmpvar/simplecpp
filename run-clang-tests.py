
import glob
import os
import subprocess

def cleanup(out):
  ret = ''
  for s in out.split('\n'):
    s = "".join(s.split())
    if len(s) == 0 or s[0] == '#':
      continue
    ret = ret + s + '\n'
  return ret

commands = []
for f in sorted(glob.glob(os.path.expanduser('~/llvm/tools/clang/test/Preprocessor/*.c*'))):

  for line in open(f, 'rt'):
    if line.startswith('// RUN: %clang_cc1 '):
      cmd = ''
      for arg in line[19:].split():
        if arg == '-E' or (len(arg) >= 3 and arg[:2] == '-D'):
          cmd = cmd + ' ' + arg
      if len(cmd) > 1:
        commands.append(cmd[1:] + ' ' + f)

# skipping tests..
skip = ['assembler-with-cpp.c',
        'builtin_line.c',
        'has_attribute.c',
        'line-directive-output.c',
        'macro_rescan2.c', # does not match mcpp output
        'microsoft-ext.c',
        '_Pragma-location.c',
        '_Pragma-dependency.c',
        '_Pragma-dependency2.c',
        '_Pragma-physloc.c',
        'pragma-pushpop-macro.c', # pragma push/pop
        'x86_target_features.c',
        'warn-disabled-macro-expansion.c']

todo = [
         # todo, low priority: wrong number of macro arguments, pragma, etc
         'header_lookup1.c',
         'macro_backslash.c',
         'macro_fn_comma_swallow.c',
         'macro_fn_comma_swallow2.c',
         'macro_fn_lparen_scan.c',
         'macro_disable.c',
         'macro_expand.c',
         'macro_expand_empty.c',
         'macro_fn_disable_expand.c',
         'macro_paste_commaext.c',
         'macro_paste_empty.c',
         'macro_paste_hard.c',
         'macro_paste_hashhash.c',
         'macro_paste_identifier_error.c',
         'macro_paste_simple.c',
         'macro_paste_spacing.c',
         'macro_rescan_varargs.c',
     
         # todo, high priority
         'c99-6_10_3_3_p4.c',
         'c99-6_10_3_4_p5.c',
         'c99-6_10_3_4_p6.c',
         'comment_save.c',
         'cxx_compl.cpp',  # if A compl B
         'cxx_not.cpp',
         'cxx_not_eq.cpp',  # if A not_eq B
         'cxx_oper_keyword_ms_compat.cpp',
         'expr_usual_conversions.c', # condition is true: 4U - 30 >= 0
         'hash_line.c',
         'macro_fn_varargs_named.c',  # named vararg arguments
         'mi_opt2.c',  # stringify
         'print_line_include.c',  #stringify
         'stdint.c',
         'stringize_misc.c']

numberOfSkipped = 0
numberOfFailed = 0

usedTodos = []

for cmd in set(commands):
  if cmd[cmd.rfind('/')+1:] in skip:
    numberOfSkipped = numberOfSkipped + 1
    continue

  clang_cmd = ['clang']
  clang_cmd.extend(cmd.split(' '))
  p = subprocess.Popen(clang_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  comm = p.communicate()
  clang_output = comm[0]

  cppcheck_cmd = [os.path.expanduser('~/cppcheck/cppcheck'), '-q']
  cppcheck_cmd.extend(cmd.split(' '))
  p = subprocess.Popen(cppcheck_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  comm = p.communicate()
  cppcheck_output = comm[0]

  if cleanup(clang_output) != cleanup(cppcheck_output):
    filename = cmd[cmd.rfind('/')+1:]
    if filename in todo:
      print('TODO ' + cmd)
      usedTodos.append(filename)
    else:
      print('FAILED ' + cmd)
      numberOfFailed = numberOfFailed + 1

for filename in todo:
    if not filename in usedTodos:
        print('FIXED ' + filename)

print('Number of tests: ' + str(len(commands)))
print('Number of skipped: ' + str(numberOfSkipped))
print('Number of todos: ' + str(len(usedTodos)))
print('Number of failed: ' + str(numberOfFailed))
