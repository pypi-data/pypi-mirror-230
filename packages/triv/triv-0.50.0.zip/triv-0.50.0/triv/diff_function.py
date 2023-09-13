original_string = """0123
456
789"""

comparison_string = """0123
456
789"""

def diff_strings(original, comparison):
  originalLines = original.split("\n")
  comparisonLines = comparison.split("\n")

  if len(originalLines) != len(comparisonLines):
    return 'Mismatch in number of lines: ' + str(len(originalLines)) + " expected and " + str(len(comparisonLines)) + " returned"
  if originalLines != [""]:
    for originalLineNum, originalLine in enumerate(originalLines):
      for originalCharNum, originalChar in enumerate(originalLine):
        comparisonLine = comparisonLines[originalLineNum]
        sideBySide = '\nOriginal Line: "{}"\nCompari. Line: "{}"'.format(originalLine, comparisonLine)
        if len(comparisonLine) == len(originalLine):
          try:
            if comparisonLine[originalCharNum] != originalChar:
              return 'Mismatch in character at line {} and character {}.{}'.format(originalLineNum+1, originalCharNum+1, sideBySide)
          except IndexError:
            return 'IndexError at line {} and character {}.{}'.format(originalLineNum, originalCharNum, sideBySide)
        else:
          return 'Mismatch in number of characters at line {}, with length {} expected, and {} returned.{}'.format(originalLineNum+1, len(originalLine), len(comparisonLine), sideBySide)
    return "No differences detected"
  else:
    return 'Mismatch in number of characters at line {}, with length {} expected, and {} returned.{}'.format(1, 0, len(comparisonLines[0]), '\nOriginal Line: ""\nCompari. Line: "{}"'.format(comparisonLines[0]))


def main():
  print(diff_strings(comparison_string, original_string))

if __name__=='__main__':
  main()
