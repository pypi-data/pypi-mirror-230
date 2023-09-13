#!/usr/bin/env python3

import sys,functools,re
from copy import deepcopy

VERSION = "0.50.0"
DEBUG = False
# short-form debug string expands to a larger set of debug options
# valid values:
# True = launch PDB at line 1
# LineNum => int = launch PDB at LineNum
# => str = launch PDB at line == str
# "print" = print count of blank lines with output
# "partial" = for use with manual PDB calls
# "_" = replace spaces with _ on output
#
# valid full option definitions:
# {"TestNum": TestNum} = launch PDB on document test of number TestNum
# {"expected": False} = do not output the expected test result

_initFalse = False
_initNone = None
_init0 = 0
_AssumptionWas = lambda _: False

'''
_curr_tests = [
[["""
""","0.0"],"""
"""],
]
'''

class ProgramConfiguration:
    def __init__(self):
        self.debug = {
            "FullTraceback": False,
            "TestNum": DEBUG.get("TestNum") if isinstance(DEBUG, dict) else None,
            "LineNum": DEBUG.get("LineNum") if isinstance(DEBUG, dict) else DEBUG if type(DEBUG) == type(0) else 1 if DEBUG == True else None,
            "LineSearch": DEBUG if isinstance(DEBUG, str) else None,
            "print": bool(DEBUG.get("print")) if isinstance(DEBUG, dict) else True if DEBUG == "print" else False,
            "partial": bool(DEBUG.get("partial")) if isinstance(DEBUG, dict) else True if DEBUG == "partial" else False,
            "_": bool(DEBUG.get("_")) if isinstance(DEBUG, dict) else True if DEBUG == "_" else False,
            "Context_Code_Lines": 5,
            "WarningVerbosity": 2,
        }

        self._mainExits = {
            FileNotFoundError: {"sysExit": "NOINPUT", "message": "File not found,{}"},
            PermissionError: {"sysExit": "IOERR", "message": "Permission denied,{}"},
            IOError: {"sysExit": "IOERR", "message": "Input/output error{}"},
            MemoryError: {"sysExit": "IOERR", "message": "Out of memory{}"},
        }

        self._progExits = {
            KeyboardInterrupt: {"sysExit": "KeyboardInterrupt", "category": "\nCanceled:", "message": "Keyboard interrupt"},
        }

        self._mainExits.update(self._progExits)

        self._sysExits = {
            "_WARNINGS": 1,
            "_EXCEPTIONS": 1,
            "Usage": 2,
            "NOINPUT": 66,
            "DATAERR": 65,
            "SOFTWARE": 70,
            "IOERR": 74,
            "CONFIG": 78,
            "KeyboardInterrupt": 130,
        }

    def _theExits(self, exception, theExits, _sysExit, *args):
        if type(exception) in theExits:
            category = theExits[type(exception)]['category'] if 'category' in theExits[type(exception)] else "Error:"
            message = theExits[type(exception)]['message'].format(*args)
            sysExit = self._sysExits[theExits[type(exception)]['sysExit']]
        else:
            category = "Error:"
            descr = exception.__doc__.strip().split("\n")[0]
            descr = descr[:-1] if descr[-1]=="." else descr
            descr = '"'+descr+'"'
            details = " and ".join(['"'+a+'"' for a in exception.args if type(a)==type("")])
            message = 'Program reported {}{}'.format(descr+(" and "+details if details else ""), *args)
            sysExit = self._sysExits[_sysExit]
        return [sysExit, category+" "+message]

    _isDebug = lambda self, sysExit: exit(sysExit) if not self.debug['FullTraceback'] else True

class TestSuite:
    def __init__(self):
        self.config = {
          "expected": bool(DEBUG.get("expected")) if isinstance(DEBUG, dict) else True,
          "verbosity": 0,
          "futureFeatures": False,
        }
        self.testno = None

    def elementTest(self, verbose=0):
        import os
        verbosity = verbose

        with open(os.path.join(os.path.dirname(__file__), "element_cases.txt")) as f:
            data = f.read()

        lines = data.split("\n")

        line_input = False
        expected_output = False
        pairs = []
        for line in lines:
            if line.lstrip().startswith(">>> ln("):
                line_input = line[line.find(">>> ln('''")+len(">>> ln('''"):line.rfind("''')")].strip()
                expected_output = True
            elif expected_output:
                expected_output = line
            else:
                expected_output = False
            if type(line_input) == type("") and type(expected_output) == type(""):
                pairs.append([line_input, expected_output])
                line_input = ""
                expected_output = False

        def testLn(theInput, theExpected):
            t = ParserTriv()
            t.program.debug['partial'] = False
            t.line = theInput.strip()
            t.lineIndex = 0
            t.ln.warningsIfDefaultToContentLn = []
            fullOutput = t.isElementStatement()
            output = t.minIsElementStatement(fullOutput)
            return output

        statusPerPair = []
        for theInput, theExpected in pairs:
            theOutput = testLn(theInput, theExpected)
            comparison = repr(theOutput)
            status = comparison == theExpected
            statusPerPair.append(status)
            textIndent = "    "
            if status == True:
                if verbosity == 0:
                    pass
                if verbosity == 1:
                    pass
                if verbosity >= 2:
                    print(str(status) + "   " + theInput)
                if verbosity >= 3:
                    print(textIndent + comparison)
                if verbosity >= 4:
                    print(textIndent + "==")
                    print(textIndent + theExpected)
            if status == False:
                if verbosity >= 0:
                    print(str(status) + "  " + theInput)
                if verbosity >= 2:
                    print(textIndent + comparison)
                    print(textIndent + "NOT")
                    print(textIndent + theExpected)

        numNotPassing = len([status for status in statusPerPair if status == False])
        if verbosity >= 2 or (verbosity == 1 and numNotPassing):
            print("")
        if verbosity >= 1:
            print("{t} element matching tests:".format(t=len(pairs)))
            print("  {p} passed and {f} failed.".format(p=len(pairs)-numNotPassing, f=numNotPassing))

    def documentTest(self, p, limited=[], ofVersionKnownGood=None):
        import document_cases
        toTest = document_cases.tests
        try:
            if toTest:
                toTest = _curr_tests
                toTest =[{"test": test,
                        "versionKnownGood": versionKnownGood,
                        "expected": expected,
                        "expectedWarningsStr": ""}
                        for i,((test,versionKnownGood),expected) in enumerate(toTest)]
        except NameError:
            pass
        VERSION=p.VERSION
        if testSuite.config["futureFeatures"]:
            VERSION="9999.9999.9999"
        fullCounter = _init0
        triesCounter = _init0
        largestVersionStrWas = "0"
        notPassingCounter = _init0
        for self.testno, testAsObj in enumerate(toTest):
            test = testAsObj['test']
            version_known_good = testAsObj['versionKnownGood']
            expected = testAsObj['expected']
            expectedWarningsStr = testAsObj['expectedWarningsStr']

            self.testno = self.testno + 1
            if program.debug['TestNum'] == self.testno and program.debug['LineNum'] is None:
                import ipdb; ipdb.set_trace(context=program.debug["Context_Code_Lines"])
            try:
                versionGeqKnownGood = p.largestVersionStr(VERSION, version_known_good) == VERSION
            except ValueError:
                print(testNumStr, "Error: version known good is not composed of numerics")
                continue
            if not versionGeqKnownGood:
                # skip tests that are meant for a later version
                continue
            if ofVersionKnownGood and version_known_good != ofVersionKnownGood:
                continue
            fullCounter += 1
            if not program.debug["TestNum"]:
                if (limited and self.testno not in limited):
                    continue
            else:
                if not program.debug["TestNum"] == self.testno:
                    continue
            largestVersionStrWas = p.largestVersionStr(largestVersionStrWas, version_known_good)
            np = ParserTriv()
            if test and test[0] == "\n":
                test = test[1:]
            if test and test[-1] == "\n":
                test = test[:-1]
            result = np.compile(test)
            expectedstr = document_cases.strip_surrounding_newlines(expected)
            testNumStr = format(self.testno,str(len(str(len(toTest)))))
            if set([n.isnumeric() for n in VERSION.split(".")]) != {True}:
                print("Error: tested version is not composed of numerics")
                break
            if not isinstance(version_known_good, str):
                print(testNumStr, "Error: version known good not a string")
                continue
            elif version_known_good == "":
                print(testNumStr, "Error: version known good is blank")
                continue
            triesCounter += 1
            warnings = [([obj['lineNum'],obj['colNum']],(obj['warningInfo'] if obj['warningInfo'] in np.warningDefs.messages else "Generic")) for obj in np.warnings]
            del np
            warningsStr = ", ".join([m+"<"+str(":".join([str(a) for a in p])+">") for p,m in warnings])
            if result == expectedstr and warningsStr == expectedWarningsStr:
                if testSuite.config['verbosity'] >= 2:
                    print(testNumStr, True)
                if testSuite.config['verbosity'] >= 3:
                    if testSuite.config['verbosity'] >= 4: print("")
                    print('"""\n'+test+'\n"""')
                    if testSuite.config['verbosity'] == 3 and warnings: print("Warnings: "+warningsStr)
                if testSuite.config['verbosity'] >= 4:
                    print("==>")
                    print('"""\n'+result+'\n"""'+(""))
                    if warnings: print("Warnings: "+warningsStr)
            else:
                notPassingCounter += 1
                print(testNumStr, False)
                print('"""\n'+test+'\n"""')
                if testSuite.config['verbosity'] >= 2:
                    print("==>")
                    if program.debug["_"]: result = result.replace(" ","_")
                    resultStr = result
                    print('"""\n'+resultStr+'\n"""'+(""))
                    if testSuite.config['expected'] and warnings: print("Warnings: "+warningsStr)
                    if testSuite.config['expected']: print("NOT")
                    if testSuite.config['expected']: print("'''\n"+expectedstr+"\n'''")
                    if testSuite.config['expected'] and (warnings or expectedWarningsStr): print("Warnings: "+(expectedWarningsStr if expectedWarningsStr else "None")+"\n")
                if testSuite.config['verbosity'] >= 5:
                    from diff_function import diff_strings
                    if testSuite.config['expected']: print('==')
                    if testSuite.config['expected']: print(diff_strings(expectedstr, result))
                    if testSuite.config['expected'] and (warningsStr != expectedWarningsStr): print(("Also" if result != expectedstr else "But") +" warnings string is different")
        if testSuite.config['verbosity'] >= 1:
            if testSuite.config['verbosity'] >= 5:
                print("")
                print("Largest version string was: " + largestVersionStrWas)
            print("")
            print("{t} document test{s} of {l}:".format(t=triesCounter, s="s" if triesCounter!=1 else "", l=fullCounter))
            print("  {p} passed and {f} failed.".format(p=triesCounter-notPassingCounter, f=notPassingCounter))

program = ProgramConfiguration()
testSuite = TestSuite()

#testSuite.config['verbosity'] = 1
#program.debug["TestNum"] = 1
#program.debug["LineNum"] = 1
#program.debug["print"] = True


class ParserTriv:

    VERSION=VERSION
    api_version=VERSION

    class const:
        outIndent = "  "  # two spaces as indents for output tags
        baseIndent = 0    # indent count added to tags and non-justified content if > 0
        defaultElementName = "div"
        delims = [":", "|"]
        modelExplicitTagDelim = delims[0]
        closers = ["/", "//"]
        prefixes = list("~!@$%^&*-_+;,?")
        postfixes = prefixes+list("#")
        prefixes = []
        reservedChSeqsInDecorator = list("""<>&'"\t#[]""")
        reservedChSeqsInDecoratorHeadingElement = list(""" """)
        reservedChSeqsInDecoratorSectionElement = list(""" /""")
        convenienceLiteral = "'"

    class Opt:
        def __init__(self):
            self.of = {
              "input": {
                "NonMatchingQuoteAndUnquotedSquareBracketInAttributeString": True,
                "AngleBracketInSectionTitle": False,
                "defaultElementName": ParserTriv.const.defaultElementName,
              },
              "output": {
                "baseIndent": ParserTriv.const.baseIndent,
                "deindentedFirstLineOfMultilineCondensedLiteral": False,
              },
              "stderr": {
                "warnings": {
                  "verbosity": program.debug['WarningVerbosity'],
                }
              }
        }

    class warningDefs:
        _Undefined = "Undefined"
        _NotImplemented = "NotImplemented"
        _NotValid = "NotValid"
        _NotByStyleGuide = "NotByStyleGuide"
        _NotRecommended = "NotRecommended"
        _NotImplementedConfig = "NotImplementedConfig"
        _NotValidConfig = "NotValidConfig"
        _NotPermittedByOption = "NotPermittedByOption"

        types = {
            _Undefined: "Undefined syntax",
            _NotImplemented: "Not implemented syntax",
            _NotValid: "Not valid syntax",
            _NotByStyleGuide: "Style guide nonuniformity",
            _NotRecommended: "Not recommended syntax",
            _NotImplementedConfig: "Not implemented config",
            _NotValidConfig: "Not valid config",
            _NotPermittedByOption: "Not permitted by config option",
        }
        messages = {
          "Undefined": [_Undefined, ""],
          "TabIndentation": [_NotImplemented, "if attempting indentation by a tab character"],
          "QuotedElementName": [_NotImplemented, "if attempting a quoted element name"],
          "DefaultSelfClosingElement": [_NotValid, "if attempting a default self-closing element"],
          "DefaultBwmElement": [_NotValid, "if attempting a default element with a blockwise mark"],
          "NativeElementOutsideOfStatementOrLiteral": [_NotValid, "if attempting to add a native element, e.g. HTML or XML, outside of a content literal or the first line of a condensed element statement"],
          "IndentedLiteralTrailingToggleOutsideOfSection": [_NotByStyleGuide, "if attempting indented output of a content or comment literal outside of a section"],
          "UnquotedSquareBracketInAttributeString": [_NotRecommended, "for a square bracket ([,]) to not be quoted in an attribute string"],
          "NonMatchingQuoteInAttributeDecorator": [_NotRecommended, "for a quote character without a matching quote character to be in a section's attribute decorator"],
          "UnquotedAngleBracketInAttributeDecorator": [_NotRecommended, "for an angle bracket (<,>) to not be quoted in a section's attribute decorator"],
          "UnquotedAmpersandInAttributeDecorator": [_NotRecommended, "for an ampersand (&) to not be quoted in a section's attribute decorator"],
          "SquareBracketInSectionTitle": [_NotValid, "if attempting a square bracket ([,]) in a section's title"],
          "AngleBracketInElementName": [_NotRecommended, "for an angle bracket (<,>) to be in an element name"],
          "AmpersandInElementName": [_NotRecommended, "for an ampersand (&) to be in an element name"],
          "LeadingForwardSlashInElementName": [_NotRecommended, "for a leading forward slash to be in an element name"],
          "TrailingForwardSlashInElementName": [_NotRecommended, "for a trailing forward slash to be in an element name"],
          "TrailingForwardSlashInAttributeString": [_NotRecommended, "for a trailing forward slash to be in an attribute string"],
          "TrailingForwardSlashInAttributeDecorator": [_NotRecommended, "for a trailing forward slash to be in a section's attribute decorator"],
          "NonMatchingQuoteInAttributeString": [_NotRecommended, "for a quote character without a matching quote character to be in an attribute string"],
          "EOFWhileContinuingLiteral": [_NotRecommended, "for a literal to not be closed before the completion of the file"],
          "NonMatchingQuoteAndQuotedDelimetingTextInAttributeString": [_NotImplemented, "if attempting ]: or ]| quoted in an attribute string while another quote character has no matching quote character"],
          "NonBlockquoteLiteral": [_NotImplemented, "if attempting a content or comment literal not on a separate line from its toggle characters"],
          "NonMatchingNativeConvenienceCloseTag": [_NotValid, "if attempting a native convenience close tag without an immediate matching native opening tag"],
          "VersionStringTooLarge": [_NotImplementedConfig, "for a value of 'api-version' to be larger than the implemented API version"],
          "NonStandardVersionString": [_NotImplementedConfig, "for a value of 'api-version' to not be composed of numerics"],
          "ConfigForOptIsNotJSON": [_NotValidConfig, "for a value of 'opt' to not be valid JSON"],
          "NonMatchingQuoteAndUnquotedSquareBracketInAttributeString": [_NotPermittedByOption, "for NonMatchingQuoteInAttributeString and UnquotedSquareBracketInAttributeString to be returned by an element statement"],
          "SingleAndDoubleQuoteInSectionIdOrTitlePropertyValue": [_NotByStyleGuide, "for both single and double quote characters to be in the title of a section with an ID mark or title property name decorator"],
          "CommentAsElementName": [_NotRecommended, "for an element name to start with an HTML or XML comment sequence (!--)"],
          "CommentAsSectionElementName": [_NotRecommended, "for a section's element name to start with an HTML or XML comment sequence (!--)"],
          "CommentAsSectionHeadingElementName": [_NotRecommended, "for a section's heading element name to start with an HTML or XML comment sequence (!--)"],
          "OmittedHeadingAndIdPropertyWithSectionElementName": [_NotByStyleGuide, "for a section's element name or ID property to be specifically omitted unless the title is a single dash character (-)"],
        }
        messages = {warning: {"type": warningType, "message": message} for warning, [warningType, message] in messages.items()}

    class Ln:
        pass

    def __init__(self):
        self.opt = self.Opt()
        self.ln = self.Ln()
        self.warnings = []
        self.program = program

    def compile(self,fileData):
        self.lenJsLn = 0
        self.data = fileData
        self.configMatter, _, source = self._.sortedDictValList(self.configMatterAndSource(fileData))
        self.lenConfigMatterLn = 0

        if self.configMatter:
            self.lenConfigMatterLn = len(self.configMatter[:-len("\n")].split("\n"))
            self.applyConfigMatter(self.configMatter)
        self.foundModelElement = False
        self.toggledFoundBlankLines = True

        # add 2ndtolastline + lastline to close any open sections and tags, respectively
        self.lines = source.rstrip().split("\n")+[""]+[""]

        #kept track of between lines
        self.compiledData = ""
        self.indents = 0
        self.lastIndent = 0
        self.nodeStack = []
        self.lenTagStack = 0
        self.currElement = _initNone
        self.lenSectionStack = 0
        self.currSection = _initNone
        self.lastOutIndent = 0
        self.blankLines = 0
        self.paddingBlankLines = 0
        self.lastOpenElementHadNoContents = True
        self.lastElementHadCondensedContent = False
        self.isContinuingLiteral = False # can be: False,'"',"'","`","!"
        self.toggledLiteralOnLn = None
        self.foundQuoteJustSign = None # can be: None, False, True
        self.convenienceLines = {}
        self.isAnySectionOpen = False
        self.sectionsNestedInThis = None
        self.isClosingSection = None
        self.condensedLiteralLine = False
        self.cache = {}
        dummy = None

        for self.lineIndex,self.line in enumerate(self.lines):
            self.lineNum = self.lineIndexToLineNum(self.lineIndex)
            self.ln.warningsIfDefaultToContentLn = []

            if ((program.debug["LineNum"] is not None and self.lineNum >= program.debug["LineNum"]) \
              or self.line.strip() == program.debug["LineSearch"]):
                if program.debug["TestNum"] is None or (program.debug["TestNum"] is not None \
                  and program.debug["TestNum"] == testSuite.testno and self.lineNum >= program.debug["LineNum"]):
                      import ipdb; ipdb.set_trace(context=program.debug["Context_Code_Lines"])
            #prospectively strip indents
            self.ln.lsLine = self.line.lstrip()
            self.ln.stLine = self.ln.lsLine.strip()
            self.ln.isBlankLine = self.ln.lsLine == ""
            self.ln.isLastLine = self.lineIndex==(len(self.lines)-1)
            self.ln.is2ndToLastLine = self.lineIndex==(len(self.lines)-2)

            if not self.ln.isBlankLine and not self.isContinuingLiteral or self.ln.isLastLine:
                self.lastIndent = self.indents
                #prospectively count indents
                self.indents = self.countIndents(self.line)

            # cleared with every newly processed line:
            self.ln.tempLineout = ""
            self.ln.lineout = ""
            self.ln.defaultToContentLine = False
            self.isToggleMultiline = False

            self.ln.isThisSectionHeading = bool(self.ln.lsLine) and not self.isContinuingLiteral and self.isSectionHeading()

            # keep nesting a new  section immediately following a closed section with no linebreak
            lastElementThatCouldGetSection = self._.noneOrPop([el for el in self.nodeStack if el['_s'] == 'tags' and el['couldGetSection']])
            isNestedSection = not self.isAnySectionOpen and \
                              self.ln.isThisSectionHeading and \
                              lastElementThatCouldGetSection

            if isNestedSection:
                self.sectionsNestedInThis = lastElementThatCouldGetSection

            if self.ln.is2ndToLastLine and self.isContinuingLiteral:
                self.warning("EOFWhileContinuingLiteral", lineNum=self.toggledLiteralOnLn)
                self.multilineOff()

            #close any tags that need to be closed
            if (not self.ln.isBlankLine and not self.isContinuingLiteral and (self.lastIndent>=self.indents or (self.ln.isThisSectionHeading and not isNestedSection))) or self.ln.isLastLine or self.ln.is2ndToLastLine:
                self.closeTags()

            # add preceding linebreaks
            if not self.ln.isBlankLine and not self.isImplicitSectionClose():
                self.toggledFoundBlankLines = False
                self.ln.tempLineout += "\n" * (self.blankLines)
                if self.currElement and self.currElement['tagindent'] < self.indents and self.currElement['paddingBlankLines'] == -1:
                    self.currElement['paddingBlankLines'] = self.blankLines
                self.paddingBlankLines = self.blankLines
                if program.debug["print"]: self.ln.tempLineout += "b*"+str(self.blankLines)
                self.blankLines = 0

            # determine if the line could toggle a multiline block
            multiline_toggles = {self.isToggleQuo1: "'", self.isToggleQuo2: '"', self.isToggleQuoV: "`", self.isToggleMsg: "!"}
            multiline_funcs = {v:k for k,v in multiline_toggles.items()}
            for isToggle in multiline_toggles:
                if isToggle(self.ln.stLine):
                    self.isToggleMultiline = multiline_toggles[isToggle]
                    break

            # process the current line
            if False:
                pass
            elif self.isToggleMultiline and not self.isContinuingLiteral:
                # begin multiline block
                self.lastOpenElementHadNoContents = False
                self.isContinuingLiteral = self.isToggleMultiline
                self.toggledLiteralOnLn = self.lineNum
                # determine if left-justified quote
                if self.foundQuoteJustSign == None and self.condensedLiteralLine is False:
                    self.foundQuoteJustSign = False
                    for i,linelookahead in enumerate(self.lines[self.lineIndex+1:]):
                        if multiline_funcs[self.isContinuingLiteral](linelookahead.strip()):
                            if linelookahead == linelookahead.lstrip():
                                self.foundQuoteJustSign = True
                                break
                        else:
                            if self.isContinuingLiteral == self.const.convenienceLiteral:
                                self.convenienceLines[self.lineIndex+1+i] = linelookahead
                    if self.isContinuingLiteral == self.const.convenienceLiteral:
                        self.convenienceLiteral()
                if self.isToggleMultiline == "!":
                    # place begin comment marker
                    self.ln.tempLineout += "\n"
                    self.ln.tempLineout += self.const.outIndent * (self.indents + self.lenSectionStack + self.opt.of['output']['baseIndent'])
                    self.ln.tempLineout += "<!--"
                else:
                    if self.currElement and not self.isAnySectionOpen: self.currElement['couldGetSection'] = False
                self.ln.lineout = self.ln.tempLineout
            elif self.isContinuingLiteral:
                if self.condensedLiteralLine is False:
                    self.lastOpenElementHadNoContents = False
                if self.isToggleMultiline and self.isContinuingLiteral == self.isToggleMultiline:
                    # end multiline block
                    self.multilineOff()
                else:
                    # regular content line in a multiline block
                    if re.fullmatch(".+"+self.isContinuingLiteral*3, self.ln.stLine):
                        self.warning("NonBlockquoteLiteral")
                    if self.condensedLiteralLine is False or self.condensedLiteralLine != self.lineIndex - 1:
                        self.ln.tempLineout = "\n"
                    if self.condensedLiteralLine is False and self.foundQuoteJustSign == False:
                        self.ln.tempLineout += self.const.outIndent * ( self.lenSectionStack + self.opt.of['output']['baseIndent'] )
                    if self.isContinuingLiteral == self.const.convenienceLiteral:
                        self.ln.tempLineout += self.convenienceLines[self.lineIndex]
                    elif self.isContinuingLiteral == "`":
                        # try to make html code safe to publish in a publication literal
                        self.ln.tempLineout += self.line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                    elif self.isContinuingLiteral == "!":
                        # try to make html comment code safe to publish in a comment literal
                        self.ln.tempLineout += self.line.replace("--","- -").replace("--","- -")
                    else:
                        self.ln.tempLineout += self.line

                self.ln.lineout = self.ln.tempLineout
            elif self.ln.isBlankLine and not self.ln.is2ndToLastLine:
                if not self.toggledFoundBlankLines:
                    self.blankLines += 1
                    self.ln.lineout = self.ln.tempLineout
            elif self.memo(self.isSectionClose) is not False or self.ln.is2ndToLastLine:
                self.closeSections(s=False,n=self.lenSectionStack if self.ln.is2ndToLastLine else self.memo(self.isSectionClose))
                # make following tags start acting like before the section was nested
                if self.sectionsNestedInThis:
                    self.indents = self.sectionsNestedInThis['tagindent']
                self.ln.lineout = self.ln.tempLineout
            elif self.ln.isThisSectionHeading:
                title,isId,sectionLvl,headingElementName,sectionElementName,propName,attributeDecorator = self.memo(self.parseSection)
                if title != None:
                    self.lastOpenElementHadNoContents = False

                    # implicitly close last open section
                    self.closeSections(sectionLvl)

                    if self.isClosingSection:
                        self.toggledFoundBlankLines = False
                        self.ln.tempLineout += "\n" * (self.blankLines)
                        self.paddingBlankLines = self.blankLines
                        self.blankLines = 0

                    # open new section
                    self.ln.tempLineout += "\n"
                    self.ln.tempLineout += self.const.outIndent * ( self.lenSectionStack + self.opt.of['output']['baseIndent'] + self.indents )
                    if attributeDecorator:
                        attributeDecorator = " "+attributeDecorator
                    if propName or isId:
                        _q = '"'
                        _t = title
                        if isId:
                            if not propName:
                                propName = "id"
                            _t = title.replace(" ","_")
                            if self.opt.of['input']['AngleBracketInSectionTitle']:
                                openTagSeen = False
                                titleIdNoTags = ""
                                lenTitleIdNoTags = 0
                                for i,ch in enumerate(_t):
                                    if ch=="<":
                                        openTagSeen = i
                                    elif openTagSeen is not False and ch==">":
                                        titleIdNoTags += _t[lenTitleIdNoTags:openTagSeen]
                                        lenTitleIdNoTags = i+1
                                        openTagSeen = False
                                    else:
                                        pass
                                titleIdNoTags += _t[lenTitleIdNoTags:]
                                _t = titleIdNoTags
                        if '"' in _t and "'" not in _t:
                            _q = "'"
                        elif "'" in _t and '"' not in _t:
                            _q = '"'
                        elif '"' in _t and "'" in _t:
                            _t = _t.replace('"', "`")
                            _q = '"'
                            self.warning("SingleAndDoubleQuoteInSectionIdOrTitlePropertyValue")
                        self.ln.tempLineout += '<'+sectionElementName+' '+propName+'='+_q+_t+_q+attributeDecorator+'>'
                    else:
                        self.ln.tempLineout += "<"+sectionElementName+attributeDecorator+">"
                    if headingElementName != "":
                        ampSeen = False
                        titleAmp = ""
                        lenTitleAmp = 0
                        for i,ch in enumerate(title):
                            if ch=="&":
                                ampSeen = i
                            elif ampSeen is not False and (ch.isalpha() or ch.isnumeric() or ch == "#"):
                                pass
                            elif ampSeen is not False and ch == ";":
                                ampSeen = False
                            elif ampSeen is not False:
                                titleAmp += title[lenTitleAmp:ampSeen+1]+"amp;"
                                lenTitleAmp = ampSeen+1
                                ampSeen = False
                            else:
                                pass
                        if ampSeen is not False:
                            titleAmp += title[lenTitleAmp:ampSeen+1]+"amp;"
                            lenTitleAmp = ampSeen+1
                        titleAmp += title[lenTitleAmp:]
                        if titleAmp[-1] == "&":
                            titleAmp += "amp;"
                        title = titleAmp
                        if not self.opt.of['input']['AngleBracketInSectionTitle']:
                            title = title.replace("<","&lt;").replace(">","&gt;")
                        self.ln.tempLineout += "<"+headingElementName+">"+title+"</"+headingElementName+">"
                    outerSecPadLines = None
                    if self.currSection and self.currSection['outerSecPadLines'] and self.currSection['outerSecPadLines'] is None:
                        self.currSection['outerSecPadLines'] = self.paddingBlankLines
                    self.nodeStack.append({"_s":"section","title":title,"sectionLvl":sectionLvl,"indents":self.indents,"sectionElementName":sectionElementName,"paddingBlankLines":self.paddingBlankLines,"outerSecPadLines":outerSecPadLines})
                    self.lenSectionStack += 1
                    self.currSection = self.nodeStack[-1]
                    self.isAnySectionOpen = True
                    self.ln.lineout = self.ln.tempLineout
                else:
                    self.ln.defaultToContentLine = True
            elif self.isSingleLineMsg():
                self.lastOpenElementHadNoContents = False
                self.ln.tempLineout += "\n"
                self.ln.tempLineout += self.const.outIndent * (self.indents + self.lenSectionStack + self.opt.of['output']['baseIndent'])
                self.ln.tempLineout += self.parseSingleLineMsg()
                self.ln.lineout = self.ln.tempLineout
            elif self.memo(self.isElementStatement) is not False:
                self.lastOpenElementHadNoContents = True
                self.lastElementHadCondensedContent = False
                isElementStatement = self.memo(self.isElementStatement)
                validSegments = [self.isValidSegment(segment) for segment in isElementStatement['segments']]
                delim = isElementStatement['delim']

                self.ln.tempLineout += "\n"

                tagListToClose = []
                elementsStr = ""
                for attrStr, postfix, prefix, selectorTagStr in [self._.sortedDictValList(validSegment) for validSegment in validSegments]:
                    # the tag, id, classlist, and attribute string
                    tagName, extraAttributes = self.parseTag(selectorTagStr)
                    if attrStr and extraAttributes:
                        attributes = extraAttributes + " " + attrStr
                    else:
                        if attrStr:
                            attributes = attrStr
                            if attrStr.rstrip().endswith("/"):
                                self.warning("TrailingForwardSlashInAttributeString")
                        else:
                            attributes = extraAttributes

                    if tagName == "":
                        tagName = self.opt.of['input']['defaultElementName']
                    else:
                        if not self.foundModelElement \
                          and self.opt.of['input']['defaultElementName'] == self.Opt().of['input']['defaultElementName'] \
                          and delim == self.const.modelExplicitTagDelim \
                          and postfix == None \
                          and attrStr is not None and attrStr == "":  # "" is not None
                            self.opt.of['input']['defaultElementName'] = tagName
                            self.foundModelElement = True
                    if prefix is None:
                        prefix = ""
                    if postfix is None:
                        postfix = ""
                    if postfix and (not attributes or (attributes and attributes[-1] not in list("""'" \t"""))):
                        postfix = " "+postfix
                    if attributes:
                        elementsStr += "<"+prefix+tagName+" "+attributes+postfix+">"
                    else:
                        elementsStr += "<"+prefix+tagName+postfix+">"
                    tagListToClose.append((prefix,tagName))
                if tagListToClose:
                    self.nodeStack.append({"_s": "tags","tags":tagListToClose,"tagindent":self.indents,"paddingBlankLines":-1, "couldGetSection": not self.isAnySectionOpen})
                    self.lenTagStack += 1
                    self.currElement = self.getCurrTag()
                trimmed = ""
                if isElementStatement['endsOnSelfClosingTag']['segment']:
                    if not isElementStatement['segments']:
                        self.lastOpenElementHadNoContents = False
                    validSegment = self.isValidSegment(isElementStatement['endsOnSelfClosingTag']['segment'])
                    attrStr, postfix, prefix, selectorTagStr = self._.sortedDictValList(validSegment)
                    tagName, extraAttributes = self.parseTag(selectorTagStr)
                    if attrStr and extraAttributes:
                        attributes = extraAttributes + " " + attrStr
                    else:
                        if attrStr:
                            attributes = attrStr
                        else:
                            attributes = extraAttributes
                    if prefix is None:
                        prefix = ""
                    if postfix is None:
                        postfix = ""
                    if postfix and (not attributes or (attributes and attributes[-1] not in list("""'" \t"""))):
                        postfix = " "+postfix
                    selfClosingChars = isElementStatement['endsOnSelfClosingTag']['closer']
                    if selfClosingChars == "/":
                        selfClosingSlash = ""
                    elif selfClosingChars == "//":
                        selfClosingSlash = "/"
                    elementsStr += "<"+prefix+tagName+(" " if attributes else "")+attributes+postfix+selfClosingSlash+">"

                elif isElementStatement['contentLine']['delimeter']:
                    self.lastElementHadCondensedContent = True
                    trimmed = isElementStatement['contentLine']['content']
                    for toggle in multiline_funcs.keys():
                      if trimmed == toggle*3:
                          self.isContinuingLiteral = trimmed[0]
                          self.toggledLiteralOnLn = self.lineNum
                          self.condensedLiteralLine = self.lineIndex
                          break
                      elif re.fullmatch( (toggle*3)+".+", trimmed):
                          self.warning("NonBlockquoteLiteral")
                          break
                    lineLengthOfMultiline = 0
                    if self.condensedLiteralLine is not False:
                        self.foundQuoteJustSign = False
                        for i,linelookahead in enumerate(self.lines[self.lineIndex+1:]):
                            if multiline_funcs[self.isContinuingLiteral](linelookahead.strip()):
                                if self._.isInRange(self.lines, i+(self.lineIndex+1)+1) \
                                  and self.countIndents(self.lines[i+(self.lineIndex+1)+1]) > self.indents \
                                  and not self.isSectionHeading(i+(self.lineIndex+1)+1):
                                    self.condensedLiteralLine = False
                                elif linelookahead == linelookahead.lstrip():
                                    self.foundQuoteJustSign = True
                                lineLengthOfMultiline = i
                                break
                            else:
                                if self.isContinuingLiteral == self.const.convenienceLiteral:
                                    self.convenienceLines[self.lineIndex+1+i] = linelookahead
                        if self.isContinuingLiteral == self.const.convenienceLiteral:
                            self.convenienceLiteral()
                if self.condensedLiteralLine is False or lineLengthOfMultiline <= 1 or not self.opt.of['output']['deindentedFirstLineOfMultilineCondensedLiteral']:
                    # add output indentation
                    self.lastOutIndent = self.indents+self.lenSectionStack+self.opt.of['output']['baseIndent']
                    self.ln.tempLineout += self.const.outIndent * self.lastOutIndent
                self.ln.tempLineout += elementsStr
                if isElementStatement['contentLine']['delimeter']:
                    if trimmed == "!!!":
                        # place begin comment marker
                        if self.condensedLiteralLine is False:
                            self.ln.tempLineout += "\n"
                            self.ln.tempLineout += self.const.outIndent * (self.indents + self.lenSectionStack + self.opt.of['output']['baseIndent'] + 1)
                        self.ln.tempLineout += "<!--"
                        if self.condensedLiteralLine is not False \
                          and ((self.lines[self.lineIndex + 1] != "" and lineLengthOfMultiline > 0) \
                          or (lineLengthOfMultiline == 1 and self.lines[self.lineIndex + 1] == "")):
                            self.ln.tempLineout += " "
                    else:
                        if self.currElement: self.currElement['couldGetSection'] = False
                    # do not print first line quote toggle
                    if not self.isContinuingLiteral:
                        self.ln.tempLineout += isElementStatement['contentLine']['content']
                self.ln.lineout = self.ln.tempLineout
                self.warnings += \
                  [{"warningInfo": warningInfo, "lineNum": self.lineNum, "colNum": 0, "details": None}
                  for warningInfo in isElementStatement['warnings']]
            else:
                self.ln.defaultToContentLine = True

            if self.ln.defaultToContentLine or self.ln.warningsIfDefaultToContentLn:
                for toggle in [ch*3 for ch in multiline_toggles.values()]:
                    if re.fullmatch(toggle+".+", self.ln.stLine):
                        self.warning("NonBlockquoteLiteral")
                        break
                if not self.lastElementHadCondensedContent:
                    self.lastOpenElementHadNoContents = False
                    if self.currElement and not self.isAnySectionOpen: self.currElement['couldGetSection'] = False
                # regular content line
                self.ln.tempLineout += "\n"
                self.ln.tempLineout += self.const.outIndent * (self.lenSectionStack + self.opt.of['output']['baseIndent'])
                self.ln.tempLineout += self.line
                self.ln.lineout = self.ln.tempLineout

            if self.lenSectionStack == 0:
                self.isAnySectionOpen = False
                self.sectionsNestedInThis = None

            self.compiledData += self.ln.lineout
            self.warnings += \
              [{"warningInfo": warningInfo, "lineNum": self.lineNum, "colNum": 0, "details": None}
              for warningInfo in self.ln.warningsIfDefaultToContentLn]
        # strip extra newline at beginning-of-file
        if self.compiledData and self.compiledData[0] == "\n":
            self.compiledData = self.compiledData[1:]

        return self.compiledData


    lineIndexToLineNum = lambda self,lineIndex: self.lenJsLn + self.lenConfigMatterLn + lineIndex+1
    getCurrTag = lambda self: [n for n in reversed(self.nodeStack) if n['_s']=='tags'][0] if [n for n in self.nodeStack if n['_s']=='tags'] else None
    getCurrSection = lambda self: [n for n in reversed(self.nodeStack) if n['_s']=='section'][0] if [n for n in self.nodeStack if n['_s']=='section'] else None

    def multilineOff(self):
        if self.isToggleMultiline == "!" or (self.isContinuingLiteral == "!" and self.ln.is2ndToLastLine):
            # place end comment marker
            if self.condensedLiteralLine is False:
                self.ln.tempLineout += "\n"
                self.ln.tempLineout += self.const.outIndent * (self.indents + self.lenSectionStack + self.opt.of['output']['baseIndent'] + (1 if self.lastElementHadCondensedContent else 0))
            else:
                if self.lines[self.lineIndex-1] != "":
                    self.ln.tempLineout += " "
            self.ln.tempLineout += "-->"
        self.isContinuingLiteral = False
        self.toggledLiteralOnLn = None
        self.foundQuoteJustSign = None
        self.condensedLiteralLine = False
        self.convenienceLines = {}

    def closeTags(self):
        poppedEnough = False
        while(self.nodeStack and self.nodeStack[-1]['_s'] == 'tags' and not poppedEnough):
            indentAwaitingPop = self.currElement['tagindent']
            if (indentAwaitingPop >= self.indents or self.ln.isThisSectionHeading or self.ln.isLastLine or self.ln.is2ndToLastLine) and not (self.sectionsNestedInThis is self.currElement and not self.ln.is2ndToLastLine):
                # close tags in reverse order
                _,_,self.paddingBlankLines,tagindent,tags = self._.sortedDictValList(self.nodeStack.pop())
                self.currElement = self.getCurrTag()
                self.lenTagStack = max(self.lenTagStack-1, 0)
                if not self.lastOpenElementHadNoContents:
                    # start on new line
                    self.ln.tempLineout += "\n"
                    # add blank line padding
                    if not self.ln.isLastLine and not self.ln.is2ndToLastLine:
                        self.ln.tempLineout += "\n" * (min(self.blankLines,self.paddingBlankLines))
                    else:
                        self.ln.tempLineout += "\n" * (self.paddingBlankLines)
                    # add output indentation
                    self.lastOutIndent = tagindent+self.lenSectionStack+self.opt.of['output']['baseIndent']
                    self.ln.tempLineout += self.const.outIndent * self.lastOutIndent
                # close multiline tags in reverse order too
                tags.reverse()
                for multiTagNo,(prefix,tag) in enumerate(tags):
                    self.ln.tempLineout += "</"+prefix+tag+">"
                self.lastOpenElementHadNoContents = False
            else:
                poppedEnough = True

    def closeSections(self,s,n=False):
        i = 0
        sectionLvl = s
        oldOldPaddingBlankLines = 0
        while self.currSection and (self.currSection['sectionLvl'] >= sectionLvl if not n else i < n):
            _,indents,outerSecPadLines,oldPaddingBlankLines,oldsectionElementName,_,self.isClosingSection = self._.sortedDictValList(self.nodeStack.pop())
            self.currSection = self.getCurrSection()
            self.lenSectionStack = max(self.lenSectionStack-1, 0)
            if not oldPaddingBlankLines:
                if outerSecPadLines:
                    self.ln.tempLineout += "\n" * min(outerSecPadLines,self.blankLines)
            self.ln.tempLineout += "\n"
            self.ln.tempLineout += self.const.outIndent * ( self.lenSectionStack + self.opt.of['output']['baseIndent'] + indents )
            self.ln.tempLineout += "</"+oldsectionElementName+">"
            if not oldPaddingBlankLines and oldOldPaddingBlankLines:
                self.toggledFoundBlankLines = False
                self.ln.tempLineout += "\n" * (self.blankLines)
                self.paddingBlankLines = self.blankLines
                self.blankLines = 0
            oldOldPaddingBlankLines = oldPaddingBlankLines
            i += 1

    def isSectionClose(self):
        # initial syntax inspection
        if self.ln.stLine == "[]*":
            return self.lenSectionStack
        if not ( self.ln.stLine.startswith("[") and self.ln.stLine.endswith("]") ):
            return False
        #returns number of sections to close
        openBrackets = 0
        for char in self.ln.lsLine:
            if char == "[":
                openBrackets += 1
            else:
                break
        closeBrackets = 0
        for char in self.ln.lsLine[openBrackets:]:
            if char == "]":
                closeBrackets += 1
            else:
                break
        return min(openBrackets,closeBrackets) if openBrackets and closeBrackets else False

    def isSectionHeading(self, l=None):
        if l is None:
            l = self.lineIndex
        lsLine = self.lines[l].lstrip()
        if lsLine[0] == "[" and lsLine[1:].find("]") > -1:
            title,isId,sectionLvl,headingElementName,sectionElementName,propName,attributeDecorator = self.memo(self.parseSection, l)
            return title != None
        else:
            return False

    def convenienceLiteral(self):
        nativeStart = False
        elemStart = False
        elemOn = False
        elemStartOff = [" ","\t", ">"]
        convenienceNativeClose = "</>"
        quoteChs = ['"', "'"]
        quoteOn = False
        commentOn = False
        inElemOpen = False
        for lineIndex,line in self.convenienceLines.items():
            returningLine = ""
            for iCh,ch in enumerate(line):
                returningLine += ch
                if not commentOn and not quoteOn \
                  and line[iCh+1-len("<!--"):iCh+1] == "<!--":
                    commentOn = iCh+1
                elif not commentOn and not quoteOn \
                  and ch in quoteChs and inElemOpen:
                    quoteOn = ch
                elif commentOn \
                  and line[iCh+1-len("-->"):iCh+1] == "-->" and iCh > commentOn+len("-->"):
                    commentOn = False
                elif quoteOn and not commentOn \
                  and ch == quoteOn:
                    quoteOn = False
                elif not commentOn and not quoteOn and ch == "<":
                    elemStart = iCh
                    inElemOpen = True
                elif not commentOn and not quoteOn \
                  and line[iCh+1-len(convenienceNativeClose):iCh+1] == convenienceNativeClose:
                    if elemOn:
                        returningLine = returningLine[:-len(convenienceNativeClose)] + "</"+elemOn+">"
                        elemOn = False
                        elemStart = False
                        inElemOpen = False
                    else:
                        self.warning("NonMatchingNativeConvenienceCloseTag", lineNum=self.lineIndexToLineNum(lineIndex))
                elif elemStart is not False and not commentOn and not quoteOn and ch in elemStartOff:
                    grp = line[elemStart+1:iCh]
                    if grp == "" or grp.startswith("/"):
                        elemOn = False
                        elemStart = False
                        if inElemOpen and ch==">":
                            inElemOpen = False
                    else:
                        elemOn = grp
                        elemStart = False
                        if inElemOpen and ch==">":
                            inElemOpen = False
            self.convenienceLines[lineIndex] = returningLine

    def isToggleQuo1(self,stLine):
        return stLine and stLine == "'''"

    def isToggleQuo2(self,stLine):
        return stLine and stLine == '"""'

    def isToggleQuoV(self,stLine):
        return stLine and stLine == '```'

    def isToggleMsg(self,stLine):
        return stLine and stLine == "!!!"

    def isSingleLineMsg(self):
        return self.ln.lsLine and self.ln.lsLine[0] == "<"

    def isSelfClosingTag(self):
        if "[" in self.ln.stLine:
            if self.ln.stLine.endswith("]/"):
                return "/"
            if self.ln.stLine.endswith("]//"):
                return "//"
        else:
            return False

    def minIsElementStatement(self, full):
        toReturn = [None, None, None, None, None]
        if full:
            toReturn[0] = full['segments']
            toReturn[1] = full['delim']
            if not full['endsOnSelfClosingTag']['segment']:
                toReturn[2] = full['contentLine']['delimeter']
                toReturn[3] = full['contentLine']['content']
            else:
                toReturn[2] = [full['endsOnSelfClosingTag']['segment']]
                toReturn[3] = full['endsOnSelfClosingTag']['closer']
            toReturn[4] = full['warnings']
        else:
            toReturn = (full, self.ln.warningsIfDefaultToContentLn)
        return tuple(item for item in toReturn)

    def isElementStatement(self):
        """
        Returns the segments, delimeters, content, and warnings for a valid line.
        Otherwise returns False and appends to self.ln.warningsIfDefaultToContentLn.
        """
        trimmed = self.line.strip() # spaces and tabs are ignored unless quoted as literals

        foundDelim = _initFalse
        initASTperLine = {"delim": "",                    # entire lineAST set to False when expected condition is not met
                          "endsOnSelfClosingTag": {"segment": None, "closer": None},
                          "temp": {"segment": "",
                                   "attribOn": False,
                                   "quoteOn": False,
                                   "quoteB": False,
                                   "lastSeenLikelyDelimIndex": None,
                                   "isTagPortionEnding": False,
                                   "branchedOnCharNum": None,
                                   "foundDelim": False},
                          "segments": [],
                          "warnings": [],
                          "defaultToContentBecause": [],
                          "contentLine": {"delimeter": None, "content": None}}

        prospectiveLineASTs = {
            delim: {
                "noneOrMatchingQuoteExpected": deepcopy(initASTperLine),
                "nonMatchingQuote": False
            }
            for delim in self.const.delims
        }

        firstOfMatches = lambda list: list[0] if len(list) > 0 else ""
        getPostfixIfNext = lambda next: firstOfMatches([postfix for postfix in self.const.postfixes if next.startswith(postfix)])
        getDelimIfNext = lambda next, delim: firstOfMatches([delim if next.startswith(delim) else ""])
        # reverse sort to ensure '//' match takes precedence over '/' to determine full closer length
        getCloserIfNext = lambda next: firstOfMatches(sorted([closer for closer in self.const.closers if next.startswith(closer)], reverse=True))

        for closer in sorted(self.const.closers, reverse=True):
            if trimmed.endswith(closer) and len(trimmed) > len(closer)+1:
                if trimmed[:-len(closer)][-1] in self.const.postfixes and trimmed[:-len(closer)][-2] == "]" or \
                  trimmed[:-len(closer)][-1] == "]":
                    for delim in self._.sortedDict(prospectiveLineASTs):
                        prospectiveLineASTs[delim]['noneOrMatchingQuoteExpected']['endsOnSelfClosingTag']['closer'] = closer
        for i,char in enumerate(trimmed):
            if char == "[":
                for delim in self._.sortedDict(prospectiveLineASTs):
                    for perQuoting, lineAST in self._.sortedDictItemList(prospectiveLineASTs[delim]):
                        if not lineAST: continue
                        if lineAST['temp']['foundDelim']: continue
                        attribOn = lineAST['temp']['attribOn']
                        quoteOn = lineAST['temp']['quoteOn']
                        segment = lineAST['temp']['segment']
                        warnings = lineAST['warnings']
                        defaultToContentBecause = lineAST['defaultToContentBecause']
                        noneOrMatchingQuoteExpected = perQuoting == 'noneOrMatchingQuoteExpected'

                        segment += char

                        if quoteOn and attribOn:
                            if noneOrMatchingQuoteExpected:     # a[""]:b["["]: or a["["]:
                                pass                            #          ^         ^
                            else:                               # a["]:b[[]: or a["[]:
                                                                #        ^         ^
                                if self.opt.of['input']['NonMatchingQuoteAndUnquotedSquareBracketInAttributeString']:
                                    pass
                                    warnings.append("UnquotedSquareBracketInAttributeString")
                                else:
                                    pass###lineAST = False
                                    warnings.append("UnquotedSquareBracketInAttributeString")
                                    defaultToContentBecause.append("NonMatchingQuoteAndUnquotedSquareBracketInAttributeString")
                        elif quoteOn and not attribOn:
                            if noneOrMatchingQuoteExpected:     # regular"[text
                                pass                            #         ^
                            else:
                                if segment.startswith(quoteOn): # "[:
                                                                # *^  * not implemented and ": not valid
                                    assert _AssumptionWas('no nonMatchingQuote and segment.startswith(quoteOn)')
                                else:                           # a["]:b[]:
                                    attribOn = True             #       ^

                        elif not quoteOn and attribOn:
                            if noneOrMatchingQuoteExpected:     # a[[]:
                                pass                            #   ^
                                warnings.append("UnquotedSquareBracketInAttributeString")
                            else:                               # a["]:b[[]:
                                                                #   *    ^    * nonMatchingQuote and !quoteOn
                                assert _AssumptionWas("no nonMatchingQuote and !quoteOn")
                        elif not quoteOn and not attribOn:
                            if noneOrMatchingQuoteExpected:     # a[]:
                                attribOn = True                 #  ^
                            else:                               # a["]:b[]:
                                                                #   *   ^     * nonMatchingQuote and !quoteOn
                                assert _AssumptionWas("no nonMatchingQuote and !quoteOn")
                        if lineAST:
                            lineAST['temp']['attribOn'] = attribOn
                            lineAST['temp']['segment'] = segment
                            lineAST['warnings'] = warnings
                            lineAST['defaultToContentBecause'] = defaultToContentBecause
                        prospectiveLineASTs[delim][perQuoting] = lineAST
            elif char == "'" or char =='"':
                for delim in self._.sortedDict(prospectiveLineASTs):
                    for perQuoting, lineAST in self._.sortedDictItemList(prospectiveLineASTs[delim]):
                        if not lineAST: continue
                        if lineAST['temp']['foundDelim']: continue
                        branching = _initFalse
                        defaultToContentBecause = lineAST['defaultToContentBecause']
                        attribOn = lineAST['temp']['attribOn']
                        quoteOn = lineAST['temp']['quoteOn']
                        quoteB = lineAST['temp']['quoteB']
                        segment = lineAST['temp']['segment']
                        noneOrMatchingQuoteExpected = perQuoting == 'noneOrMatchingQuoteExpected'
                        freshlyBranched = not noneOrMatchingQuoteExpected and lineAST['temp']['branchedOnCharNum'] == i
                        if freshlyBranched: continue

                        if quoteOn == char and attribOn:
                            if noneOrMatchingQuoteExpected:         # a[""]:
                                quoteOn = False                     #    ^
                                if prospectiveLineASTs[delim]['nonMatchingQuote'] and not prospectiveLineASTs[delim]['nonMatchingQuote']['temp']['isTagPortionEnding']: # not a["]: n"]
                                    prospectiveLineASTs[delim]['nonMatchingQuote'] = False                                                                              #            ^
                            else:                                   # a["]:a["]:
                                lineAST = False                     #        ^
                        elif quoteOn == char and not attribOn:
                            if noneOrMatchingQuoteExpected:
                                if segment.startswith(quoteOn):     # "a":                       or "":
                                                                    # * ^   * not implemented       *^
                                    assert 'QuotedElementName' in defaultToContentBecause
                                    quoteOn = False
                                else:                               # a"":
                                                                    #  *^   * not valid
                                    assert _AssumptionWas('*"* not valid')
                            else:
                                if isTagPortionEnding:              # a["]: n"]
                                    pass                            #        ^
                                else:                               # a["]:"a":
                                    lineAST = False                 #      ^

                        elif not quoteOn == char and attribOn:
                            if noneOrMatchingQuoteExpected:
                                if not quoteOn:                     # a[""]:
                                    quoteOn = char                  #   ^
                                    branching = True                # a["]:
                                                                    #   ^
                                else:                               # a["''"]
                                    pass                            #    ^
                                    quoteB = char
                            else:
                                if quoteOn:                         # a["'']:
                                    pass                            #    ^
                                    quoteB = char
                                else:                               # a["]:a["]:
                                                                    #   *    ^  * nonMatchingQuote and !quoteOn
                                    assert _AssumptionWas("no nonMatchingQuote and !quoteOn")
                        elif not quoteOn == char and not attribOn:
                            if noneOrMatchingQuoteExpected:
                                if segment == "":                   # "a":
                                    quoteOn = char                  # ^     # not implemented
                                    defaultToContentBecause.append("QuotedElementName")
                                else:                               # a"":
                                    lineAST = False                 #  ^    # not valid

                            else:
                                if quoteOn:                         
                                    if segment == "":               # a["]:'':
                                        pass                        #      ^
                                        defaultToContentBecause.append("QuotedElementName")
                                    else:
                                        if segment.startswith(char):  # a["]:'':
                                                                      #       ^
                                            assert "QuotedElementName" in defaultToContentBecause
                                            pass
                                        else:                       # a["]:b'':
                                            lineAST = False         #       ^  # not valid
                                else:                               # a["]:"":
                                                                    #   *  ^  * nonMatchingQuote and !quoteOn
                                    assert _AssumptionWas("no nonMatchingQuote and !quoteOn")

                        segment += char
                        if lineAST:
                            lineAST['temp']['quoteOn'] = quoteOn
                            lineAST['temp']['quoteB'] = quoteB
                            lineAST['temp']['segment'] = segment
                            lineAST['defaultToContentBecause'] = defaultToContentBecause
                        prospectiveLineASTs[delim][perQuoting] = lineAST
                        if branching:
                            prospectiveLineASTs[delim]['nonMatchingQuote'] = deepcopy(lineAST)
                            prospectiveLineASTs[delim]['nonMatchingQuote']['temp']['branchedOnCharNum'] = i
                            prospectiveLineASTs[delim]['nonMatchingQuote']['warnings'].append("NonMatchingQuoteInAttributeString")
            elif char == "]":
                for delim in self._.sortedDict(prospectiveLineASTs):
                    for perQuoting, lineAST in self._.sortedDictItemList(prospectiveLineASTs[delim]):
                        if not lineAST: continue
                        if lineAST['temp']['foundDelim']: continue
                        attribOn = lineAST['temp']['attribOn']
                        quoteOn = lineAST['temp']['quoteOn']
                        quoteB = lineAST['temp']['quoteB']
                        segment = lineAST['temp']['segment']
                        warnings = lineAST['warnings']
                        defaultToContentBecause = lineAST['defaultToContentBecause']
                        isTagPortionEnding = lineAST['temp']['isTagPortionEnding']
                        noneOrMatchingQuoteExpected = perQuoting == 'noneOrMatchingQuoteExpected'
                        isSegmentEnding, isSpaceOrTabOrLfNext = [False, False]

                        segment += char

                        isSpaceOrTabOrLfNext = _initFalse
                        isPostfixNext = getPostfixIfNext(next=trimmed[i+1:])
                        isDelimNext = getDelimIfNext(next=trimmed[i+1+len(isPostfixNext):], delim=delim)

                        isCloserNext = getCloserIfNext(next=trimmed[i+1+len(isPostfixNext):])
                        isPostfixAndDelimNext = isPostfixNext+isDelimNext if isPostfixNext and isDelimNext else ""
                        isPostfixAndCloserNext = isPostfixNext+isCloserNext if isPostfixNext and isCloserNext else ""
                        if isPostfixAndDelimNext: isDelimNext = ""
                        if isPostfixAndCloserNext: isCloserNext = ""
                        # expected: a single non-empty string item
                        elementEndingStrs = [isDelimNext, isPostfixAndDelimNext, isCloserNext, isPostfixAndCloserNext]
                        listOfElementEndingStrs = [endStr for endStr in elementEndingStrs if endStr]
                        assert len(listOfElementEndingStrs) <= 1

                        isSegmentEnding = bool(listOfElementEndingStrs)
                        if isSegmentEnding:
                            lenTilSegmentEnd = len(listOfElementEndingStrs[0])
                            isSpaceOrTabOrLfNext = trimmed[i+1+lenTilSegmentEnd:i+2+lenTilSegmentEnd].rstrip() == "" # a:\s or a:\t or a:\n

                        if not quoteOn or not noneOrMatchingQuoteExpected:
                            isTagPortionEnding = isSpaceOrTabOrLfNext

                        if quoteOn and attribOn:
                            if noneOrMatchingQuoteExpected:     # a["]"]:
                                pass                            #    ^
                            else:
                                if isSegmentEnding:             # a["]: or a["]:b]]: or a["]]:
                                    attribOn = False            #    ^  or       ^         ^
                                else:                           # a["]%%: or a["]:b[]%%: or a["[]%%: not a["]:a"]:
                                                                #    ^    or        ^           ^           ^
                                    if self.opt.of['input']['NonMatchingQuoteAndUnquotedSquareBracketInAttributeString']:
                                        pass
                                        warnings.append("UnquotedSquareBracketInAttributeString")
                                    else:
                                        pass ###lineAST = False
                                        warnings.append("UnquotedSquareBracketInAttributeString")
                                        defaultToContentBecause.append("NonMatchingQuoteAndUnquotedSquareBracketInAttributeString")
                        elif quoteOn and not attribOn:
                            if noneOrMatchingQuoteExpected:     # "]":
                                                                # *^  * not implemented
                                if segment.startswith(quoteOn):
                                    assert defaultToContentBecause
                                else:                                        # a"]":
                                    assert _AssumptionWas('*"* not valid')   #  *^  * not valid
                            else:
                                if segment.startswith(quoteOn): # "]:
                                                                # *^  * not implemented and ": not valid
                                    assert _AssumptionWas('no nonMatchingQuote and segment.startswith(quoteOn)')
                                else:                           # a["]:]:
                                    pass                        #      * not valid
                                    if quoteB:
                                        segmentsStr = delim.join(lineAST['segments'])
                                        sinceQuoteAStr = segmentsStr[segmentsStr.rfind(lineAST['temp']['quoteOn'])+1:]
                                        sinceQuoteBIndex = sinceQuoteAStr.rfind(lineAST['temp']['quoteB'])
                                        if sinceQuoteBIndex > -1:
                                            sinceQuoteBStr = sinceQuoteAStr[sinceQuoteBIndex:]
                                            segmentBeforeQuoteBIndex = segment.find(quoteB)
                                            segmentAtQuoteB = segment[:segmentBeforeQuoteBIndex+1]
                                            if segmentBeforeQuoteBIndex > -1 and self.isQuotedPortionAndMatchingQuote(sinceQuoteBStr + delim + segmentAtQuoteB, char):
                                                defaultToContentBecause.append("NonMatchingQuoteAndQuotedDelimetingTextInAttributeString")
                                                if "QuotedElementName" in defaultToContentBecause: defaultToContentBecause.remove("QuotedElementName")
                                            else:
                                                lineAST = False
                                        else:
                                            lineAST = False
                                    else:
                                        lineAST = False

                        elif not quoteOn and attribOn:
                            if noneOrMatchingQuoteExpected:
                                if isSegmentEnding:             # a[]:
                                    attribOn = False            #   ^
                                else:                           # a[]]:     or a[]%%:
                                    pass                        #   ^            ^  *
                                    warnings.append("UnquotedSquareBracketInAttributeString")
                            else:                               # a["]:[]:
                                                                #   *   ^  * nonMatchingQuote and !quoteOn
                                assert _AssumptionWas("no nonMatchingQuote and !quoteOn")
                        elif not quoteOn and not attribOn:
                            if noneOrMatchingQuoteExpected:     # ]:
                                lineAST = False                 # ^
                            else:                               # a["]:]:
                                                                #   *  ^  * nonMatchingQuote and !quoteOn
                                assert _AssumptionWas("no nonMatchingQuote and !quoteOn")
                        if lineAST:
                            lineAST['temp']['attribOn'] = attribOn
                            lineAST['temp']['segment'] = segment
                            lineAST['warnings'] = warnings
                            lineAST['temp']['isTagPortionEnding'] = isTagPortionEnding
                            lineAST['defaultToContentBecause'] = defaultToContentBecause
                        prospectiveLineASTs[delim][perQuoting] = lineAST
            elif char in self.const.delims or (char in [c[0] for c in self.const.closers]):
                for delim in self._.sortedDict(prospectiveLineASTs):
                    for perQuoting, lineAST in self._.sortedDictItemList(prospectiveLineASTs[delim]):
                        if not lineAST: continue
                        if lineAST['temp']['foundDelim']: continue
                        segments = lineAST['segments']
                        endsOnSelfClosingTag = lineAST['endsOnSelfClosingTag']
                        lastSeenLikelyDelimIndex = lineAST['temp']['lastSeenLikelyDelimIndex']
                        isTagPortionEnding = lineAST['temp']['isTagPortionEnding']
                        contentLine = lineAST['contentLine']
                        attribOn = lineAST['temp']['attribOn']
                        quoteOn = lineAST['temp']['quoteOn']
                        segment = lineAST['temp']['segment']
                        warnings = lineAST['warnings']
                        defaultToContentBecause = lineAST['defaultToContentBecause']
                        noneOrMatchingQuoteExpected = perQuoting == 'noneOrMatchingQuoteExpected'

                        if char == delim and not attribOn and (not quoteOn or not noneOrMatchingQuoteExpected):
                            if not isTagPortionEnding:          # a:  not a[]:  and not  a[]_:
                                                                #  ^         ^               ^
                                isSpaceOrTabOrLfNext = trimmed[i+1:i+2].strip() == ""
                                isTagPortionEnding = isSpaceOrTabOrLfNext
                        if char == delim and not attribOn and not quoteOn:
                            segments.append(segment)
                            segment = ""
                            lastSeenLikelyDelimIndex = i
                            if isTagPortionEnding:
                                contentLine['content'] = trimmed[i+1:].lstrip()
                                contentLine['delimeter'] = trimmed[i+1:i+1+len(trimmed[i+1:])-len(contentLine['content'])]
                                for otherDelim, otherModes in self._.sortedDictItemList(prospectiveLineASTs):
                                    for otherMode in self._.sortedDict(otherModes):
                                        if otherDelim != char: prospectiveLineASTs[otherDelim] = {mode: False for mode in self._.sortedDict(prospectiveLineASTs[otherDelim])}
                                        if otherMode != perQuoting: prospectiveLineASTs[otherDelim][otherMode] = False
                        elif char == delim and not attribOn and quoteOn and not noneOrMatchingQuoteExpected:
                            segments.append(segment)
                            segment = ""
                            lastSeenLikelyDelimIndex = i
                            #                                 | # a["]:b: n  not  a["]:a: "]:
                            #                                 v #       ^               ^
                            if isTagPortionEnding:
                                contentLine['content'] = trimmed[i+1:].lstrip()
                                contentLine['delimeter'] = trimmed[i+1:i+1+len(trimmed[i+1:])-len(contentLine['content'])]
                        elif char in [c[0] for c in self.const.closers] and \
                          trimmed[i:] == endsOnSelfClosingTag['closer']:
                            if (segment[-1] == "]" or (segment[-1] in self.const.postfixes and segment[-2] == "]")) \
                              and segment[0] in ['[','.','#']:  # []// or .[]// or #[]//
                                defaultToContentBecause.append("DefaultSelfClosingElement")
                            endsOnSelfClosingTag['segment'] = segment
                            segment = ""
                        elif char in [c[0] for c in self.const.closers] and \
                          trimmed[i:] != endsOnSelfClosingTag['closer']:
                            if "[" in segment and not attribOn:
                                lineAST = False
                            else:
                                segment += char
                        else:
                            segment += char
                        if delim == "|" and segments and ( \
                            segments[-1] == "" \
                            or segments[-1] in self.const.postfixes \
                            or segments[-1][0] in ['[','.','#'] \
                          ):                                    # |  or  ?|  or  []|  or .|  or #|
                            defaultToContentBecause.append("DefaultBwmElement")
                        if lineAST:
                            if isTagPortionEnding:
                                lineAST['temp']['foundDelim'] = True
                            lineAST['temp']['segment'] = segment
                            lineAST['segments'] = segments
                            lineAST['contentLine'] = contentLine
                            lineAST['temp']['isTagPortionEnding'] = isTagPortionEnding
                            lineAST['endsOnSelfClosingTag'] = endsOnSelfClosingTag
                            lineAST['temp']['lastSeenLikelyDelimIndex'] = lastSeenLikelyDelimIndex
                            lineAST['defaultToContentBecause'] = defaultToContentBecause
                        prospectiveLineASTs[delim][perQuoting] = lineAST
            elif char == " " or char == "\t":
                for delim in self._.sortedDict(prospectiveLineASTs):
                    for perQuoting, lineAST in self._.sortedDictItemList(prospectiveLineASTs[delim]):
                        if not lineAST: continue
                        attribOn = lineAST['temp']['attribOn']
                        quoteOn = lineAST['temp']['quoteOn']
                        if not quoteOn and not attribOn:
                            lineAST = False
                        elif not lineAST['temp']['isTagPortionEnding']:
                            lineAST['temp']['segment'] += char
                        prospectiveLineASTs[delim][perQuoting] = lineAST
            else:
                for delim in self._.sortedDict(prospectiveLineASTs):
                    for perQuoting, lineAST in self._.sortedDictItemList(prospectiveLineASTs[delim]):
                        if not lineAST: continue
                        lineAST['temp']['segment'] += char
                        prospectiveLineASTs[delim][perQuoting] = lineAST
            parsableDelims = []
            foundDelims = []
            for delim, modes in self._.sortedDictItemList(prospectiveLineASTs):
                for perQuoting, lineAST in self._.sortedDictItemList(modes):
                    if lineAST:
                        parsableDelims.append((delim, perQuoting))
                        if lineAST['temp']['foundDelim']:
                            foundDelims.append((delim, perQuoting))
            if parsableDelims == []:
                foundDelim = False
                break
            elif i == len(trimmed)-1 or (len(foundDelims) == 1 and len(parsableDelims) == 1):
                for delim in self._.sortedDict(prospectiveLineASTs):
                    for perQuoting, lineAST in self._.sortedDictItemList(prospectiveLineASTs[delim]):
                        if not lineAST: continue
                        foundDelim = lineAST['temp']['foundDelim']
                        if not foundDelim:
                            lineAST = False
                        prospectiveLineASTs[delim][perQuoting] = lineAST
                everySegment = lambda lineAST: lineAST['segments'] + ([lineAST['endsOnSelfClosingTag']['segment']] if lineAST['endsOnSelfClosingTag']['segment'] else [])
                for delim in self._.sortedDict(prospectiveLineASTs):                                       # a:a|b[]//  or  a|a:b[]//
                    for perQuoting, lineAST in self._.sortedDictItemList(prospectiveLineASTs[delim]):
                        if not lineAST: continue
                        quoteOn = lineAST['temp']['quoteOn']
                        quoteB = lineAST['temp']['quoteB']
                        """
                        nonMatchingQuoteSortByLargestLastSeenLikelyDelimIndex = False
                        if self.opt.of['input']['NonMatchingQuoteAndUnquotedSquareBracketInAttributeString'] \
                          and ( set([bool(mode['nonMatchingQuote']) for mode in prospectiveLineASTs.values()]) == {True} and set([bool(mode['noneOrMatchingQuoteExpected']) for mode in prospectiveLineASTs.values()]) == {False} ):
                            nonMatchingQuoteSortByLargestLastSeenLikelyDelimIndex = True
                        """
                        if "NonMatchingQuoteInAttributeString" in lineAST['warnings'] and "UnquotedSquareBracketInAttributeString" in lineAST['warnings']:
                            quoted = False
                            for segment in everySegment(lineAST):
                                if segment[-1] == "]" or segment[-2] == "]":
                                    attrStr = segment[segment.find("[")+1:segment.rfind("]")]
                                    sinceQuoteAStr = attrStr[attrStr.rfind(quoteOn)+1:]
                                    if "[" in sinceQuoteAStr:
                                        if self.isQuotedPortionAndMatchingQuote(sinceQuoteAStr,"["):
                                            quoted = True
                                        else:
                                            quoted = False
                                            break
                                    if "]" in sinceQuoteAStr:
                                        if self.isQuotedPortionAndMatchingQuote(sinceQuoteAStr,"]"):
                                            quoted = True
                                        else:
                                            quoted = False
                                            break
                            if quoted:
                                if "NonMatchingQuoteAndUnquotedSquareBracketInAttributeString" in lineAST['defaultToContentBecause']:
                                    prospectiveLineASTs[delim][perQuoting]['defaultToContentBecause'].remove("NonMatchingQuoteAndUnquotedSquareBracketInAttributeString")
                                prospectiveLineASTs[delim][perQuoting]['warnings'].remove("UnquotedSquareBracketInAttributeString")
                        if "NonMatchingQuoteInAttributeString" in lineAST['warnings'] and "UnquotedSquareBracketInAttributeString" in lineAST['warnings']:
                            quoted = False
                            for segment in everySegment(lineAST):
                                if segment[-1] == "]" or segment[-2] == "]":
                                    attrStr = segment[segment.find("[")+1:segment.rfind("]")]
                                    if "[" in attrStr:
                                        if self.isQuotedPortionAndMatchingQuote(attrStr, "["):
                                            quoted = True
                                        else:
                                            quoted = False
                                            break
                                    if "]" in attrStr:
                                        if self.isQuotedPortionAndMatchingQuote(attrStr, "]"):
                                            quoted = True
                                        else:
                                            quoted = False
                                            break
                            if quoted:
                                prospectiveLineASTs[delim][perQuoting]['warnings'].remove("UnquotedSquareBracketInAttributeString")
                                if "NonMatchingQuoteAndUnquotedSquareBracketInAttributeString" in prospectiveLineASTs[delim][perQuoting]['defaultToContentBecause']:
                                    prospectiveLineASTs[delim][perQuoting]['defaultToContentBecause'].remove("NonMatchingQuoteAndUnquotedSquareBracketInAttributeString")
                        if not self.opt.of['input']['NonMatchingQuoteAndUnquotedSquareBracketInAttributeString'] \
                          and "NonMatchingQuoteAndUnquotedSquareBracketInAttributeString" in lineAST['defaultToContentBecause'] \
                          and False in [bool(mode[perQuoting]['defaultToContentBecause']) for mode in prospectiveLineASTs.values() if mode[perQuoting]]:
                            prospectiveLineASTs[delim][perQuoting] = False
                            continue                                                                       # a["]:b: ]|
                        elif self.opt.of['input']['NonMatchingQuoteAndUnquotedSquareBracketInAttributeString'] \
                          and "NonMatchingQuoteInAttributeString" in lineAST['warnings'] and "UnquotedSquareBracketInAttributeString" in lineAST['warnings'] \
                          and False in [("NonMatchingQuoteInAttributeString" in mode[perQuoting]['warnings'] and "UnquotedSquareBracketInAttributeString" in mode[perQuoting]['warnings']) for mode in prospectiveLineASTs.values() if mode[perQuoting]]:
                            prospectiveLineASTs[delim][perQuoting] = False
                            continue                                                                       # a["]:b: ]|
                        if lineAST['endsOnSelfClosingTag']['closer']:                                      # a:a|b[]//
                            byLargestLastSeenLikelyDelimIndex = sorted(self._.sortedDictItemList(prospectiveLineASTs), key=lambda item: item[1][perQuoting]['temp']['lastSeenLikelyDelimIndex'] if item[1][perQuoting] and item[1][perQuoting]['temp']['lastSeenLikelyDelimIndex'] else -1, reverse=True)
                            delimOfLargestLastSeenLikelyDelimIndex = byLargestLastSeenLikelyDelimIndex[0][0]
                            for otherDelim in self._.sortedDict(prospectiveLineASTs):
                                if otherDelim != delimOfLargestLastSeenLikelyDelimIndex: prospectiveLineASTs[otherDelim][perQuoting] = False
                            break

                countLineASTs = 0
                returnedLineAST = _initNone
                thesortedDict = self._.sortedDict(prospectiveLineASTs)
                for delim in thesortedDict:
                    thesortedDictItemList = self._.sortedDictItemList(prospectiveLineASTs[delim])
                    for perQuoting, lineAST in thesortedDictItemList:
                        if lineAST:
                            countLineASTs += 1
                            returnedLineAST = lineAST
                            returnedLineAST['delim'] = delim
                            returnedLineAST['quotingMode'] = perQuoting
                            returnedLineAST['warnings'] = self._.uniqueList(returnedLineAST['warnings'])
                if countLineASTs == 0:      # [: => content
                    foundDelim = False
                    break
                assert countLineASTs == 1

                if "NonMatchingQuoteInAttributeString" in returnedLineAST['warnings'] and returnedLineAST['temp']['quoteB']:
                    elementPortion = returnedLineAST['delim'].join(returnedLineAST['segments'])
                    isLastSegmentNonMatchingQuoteB = len([ch for ch in everySegment(returnedLineAST)[-1] if everySegment(returnedLineAST) and ch==returnedLineAST['temp']['quoteB']]) % 2 > 0
                    delimetedAfterLastSegment = -1
                    if returnedLineAST['contentLine']['content']:
                        delimetedAfterLastSegment = returnedLineAST['contentLine']['content'].find("]"+returnedLineAST['delim'])
                    if isLastSegmentNonMatchingQuoteB and delimetedAfterLastSegment > -1:
                        elementPortion += returnedLineAST['delim'] + returnedLineAST['contentLine']['delimeter']
                        elementPortion += returnedLineAST['contentLine']['content'][:delimetedAfterLastSegment+1]
                    elementPortion += returnedLineAST['delim']
                    if re.fullmatch("""\S*.*'[^"]*\][:\|][^"]*'.*\S*""" if quoteB == "'" else """\S*.*"[^']*\][:\|][^']*".*\S*""",elementPortion):
                        returnedLineAST['defaultToContentBecause'].append("NonMatchingQuoteAndQuotedDelimetingTextInAttributeString")
                        pass

                if returnedLineAST and not program.debug['partial']: del returnedLineAST['temp']
                foundDelim = returnedLineAST
                break

        if foundDelim and "\t" in self.line[:-len(trimmed)]:
            foundDelim['defaultToContentBecause'].append("TabIndentation")

        if foundDelim and foundDelim['defaultToContentBecause']:
            self.ln.warningsIfDefaultToContentLn += self._.uniqueList(foundDelim['defaultToContentBecause'])
            foundDelim = False
        if program.debug['partial']:
            output = self.minIsElementStatement(foundDelim)
            outputStr = str(output)
            if [item for item in self._.getFlat(output) if item and "'" in item and '"' in item]:
                outputStr = outputStr.replace("\\'","\\\\'")
            print(outputStr)

        return foundDelim

    def isValidSegment(self, segment):
        toReturn = {"prefix": None, "selectorTagStr": None, "attrStr": None, "postfix": None}
        if segment and segment[0] in self.const.prefixes:
            toReturn['prefix'] = segment[0]
            segment = segment[1:]
        if segment and segment[-1] in self.const.postfixes:
            toReturn['postfix'] = segment[-1]
            segment = segment[:-1]
        if segment and segment[-1] == "]":
            attrStrBeginning = segment.find("[")
            if attrStrBeginning == -1:
                assert _AssumptionWas("*]: -> !isElementStatement()")
            toReturn['selectorTagStr'] = segment[:attrStrBeginning]
            toReturn['attrStr'] = segment[attrStrBeginning+1:-1]
        else:
            toReturn['selectorTagStr'] = segment
        return toReturn

    def parseSingleLineMsg(self):
        tempLineout = ""
        msg = self.ln.lsLine[1:]
        # try to make html comment code safe to publish as a single-line comment
        if msg.startswith("-"):
          msg = " " + msg
        msg = msg.replace("--","- -").replace("--","- -")
        tempLineout += "<!--" + msg
        paddingSpaces = " "*(len(msg)-len(msg.lstrip()))
        tempLineout += paddingSpaces
        tempLineout += "-->"
        if re.match('<\S[\s\S]*\s*>',self.ln.lsLine):
          if re.match('<meta\s+charset="utf-8"\s*[/]?\s*>',self.line.strip().lower()) \
            or re.match("<meta\s+charset='utf-8'\s*[/]?\s*>",self.line.strip().lower()):
              pass
          else:
            self.warning("NativeElementOutsideOfStatementOrLiteral")
        return tempLineout

    def isQuotedPortionAndMatchingQuote(self, string, portion):
        # also returns False is non matching quoting mode is detected
        # if portion is "", only returns False if non matching quoting mode is detected
        if portion not in string:
            return None
        i = 0
        quoteChs = ['"', "'"]
        quoteOn = False
        while (i < len(string)):
            ch = string[i]
            if ch in quoteChs:
                if quoteOn == False:
                    quoteOn = ch
                elif quoteOn == ch:
                    quoteOn = False
            if portion and string[i:].startswith(portion):
                if quoteOn == False:
                    return False
                elif quoteOn not in string[i+len(portion):]:
                    return False
            i+=1
        if quoteOn:
            return False
        return True

    def parseSection(self, l=None):
        if l is None:
            l = self.lineIndex
        trimmed = self.lines[l].strip()
        title = trimmed[1:trimmed.index("]")]
        for ch in trimmed[trimmed.index("]")+1:]:
            if ch == "]":
                title += ch
            else:
                break
        decorator = trimmed[1+len(title)+1:]
        periodFoundStart = 0
        addlBracketOpen = 0
        for char in title:
            if char == ".":
                periodFoundStart += 1
            elif char == "[":
                addlBracketOpen += 1
            else:
                break
        periodFoundEnd = 0
        addlBracketClose = 0
        for ichar in range(1,len(title)+1):
            if title[-ichar] == ".":
                periodFoundEnd += 1
            elif title[-ichar] == "]":
                addlBracketClose += 1
            else:
                break
        if periodFoundStart:
            # descending section
            minPeriodFound = min(periodFoundStart,periodFoundEnd)
        else:
            # ascending section (or section)
            minPeriodFound = min(addlBracketOpen,addlBracketClose)
        title = title[minPeriodFound:len(title)-minPeriodFound]
        if not periodFoundStart:
            # ascending section
            minPeriodFound = -minPeriodFound
        # parse decorator
        isId = False
        headingElementName = "h1"
        sectionElementName = "div"
        propName = ""
        attributeDecorator = ""
        _l = 0
        if decorator:
            sectionElementName = None
            if decorator[0] == "#":
                isId = True
                decorator = decorator[1:]
            elif len(decorator.lstrip()) >= len(decorator) - 2 \
              and decorator.lstrip().startswith("#"):
                _l = decorator.find("#")
                isId = True
                decorator = decorator[_l+1:]
            splitresult = decorator.split("/", 1)
            if "&" in splitresult[0]:
                splitresult = [decorator]
            headingElementName = splitresult[0]
            if len(headingElementName.lstrip()) >= len(headingElementName) - (2 - _l):
                headingElementName = headingElementName.lstrip()
            if len(splitresult) > 1:
                sectionElementName = splitresult[1]
            else:
                sectionElementName = ""
            if sectionElementName:
                splitresult = sectionElementName.split(" ")
            else:
                splitresult = headingElementName.split(" ")
            if len(splitresult) > 1:
                if not sectionElementName:
                    headingElementName = splitresult[0]
                else:
                    sectionElementName = splitresult[0]
                passedOnAttrAmp = False
                for s in splitresult[1:]:
                    if not propName.strip() and headingElementName != "&":
                        if s:
                            propName += s
                        else:
                            propName += " "
                    else:
                        if s:
                            if not attributeDecorator and s=="&" and not (headingElementName=="&" or propName=="&"):
                                pass
                                passedOnAttrAmp = True
                            elif passedOnAttrAmp and s.strip()=="":
                                pass
                                passedOnAttrAmp = False
                            else:
                                passedOnAttrAmp = False
                                if attributeDecorator:
                                    attributeDecorator += " "+s
                                else:
                                    attributeDecorator = s
                        else:
                            attributeDecorator += " "
            if propName.strip() == "&":
                if attributeDecorator:
                  attributeDecorator = propName[:propName.find("&")] + attributeDecorator
                propName = ""
            elif "&" in headingElementName and not sectionElementName:
                if attributeDecorator:
                    if not isId:
                        headingElementName = "h1"
                    else:
                        headingElementName = ""
                else:
                    attributeDecorator = headingElementName[headingElementName.find("&")+1:]
                    if attributeDecorator.startswith(" "):
                        attributeDecorator = attributeDecorator[1:]
                    if headingElementName[:headingElementName.find("&")]:
                        headingElementName = headingElementName[:headingElementName.find("&")]
                    else:
                        headingElementName = "" if isId else "h1"
                    if propName:
                        attributeDecorator = (attributeDecorator+" " if attributeDecorator else "") + propName
                        propName = "id" if isId else ""
            elif "&" in sectionElementName:
                if propName:
                    attributeDecorator = propName
                    propName = "id" if isId else ""
                else:
                    attributeDecorator = sectionElementName[sectionElementName.find("&")+1:]
                sectionElementName = sectionElementName[:sectionElementName.find("&")]
            elif "&" in propName:
                attributeDecorator = propName[propName.find("&")+1:]
                propName = "id" if isId else ""
            if not sectionElementName:
                sectionElementName = "div"
        # element matching is not yet refactored before section
        np = ParserTriv()
        np.line = trimmed
        np.ln.warningsIfDefaultToContentLn = []
        if np.isElementStatement():
            title = None
        if title == None or title.strip() == "" \
          or sectionElementName == "" \
          or ((decorator and decorator[0:3-_l].strip()=="") if isId else (decorator and decorator[0:3].strip()=="")) \
          or True in [ch in self.const.reservedChSeqsInDecorator or ch in self.const.reservedChSeqsInDecoratorHeadingElement for ch in headingElementName] \
          or True in [ch in self.const.reservedChSeqsInDecorator or ch in self.const.reservedChSeqsInDecoratorSectionElement for ch in sectionElementName] \
          or True in [ch in self.const.reservedChSeqsInDecorator for ch in propName]:
            title = None # is not section heading
        if title:
            if "[" in title or "]" in title:
                title = None
                self.ln.warningsIfDefaultToContentLn.append("SquareBracketInSectionTitle")
            else:
                if self.isQuotedPortionAndMatchingQuote(attributeDecorator,"") == False:
                    self.warning("NonMatchingQuoteInAttributeDecorator")
                else:
                    if self.isQuotedPortionAndMatchingQuote(attributeDecorator,"<") == False:
                        self.warning("UnquotedAngleBracketInAttributeDecorator")
                    if self.isQuotedPortionAndMatchingQuote(attributeDecorator, ">") == False:
                        self.warning("UnquotedAngleBracketInAttributeDecorator")
                    if self.isQuotedPortionAndMatchingQuote(attributeDecorator, "&") == False:
                        self.warning("UnquotedAmpersandInAttributeDecorator")
                    if attributeDecorator.rstrip().endswith("/"):
                        self.warning("TrailingForwardSlashInAttributeDecorator")
            if headingElementName and headingElementName.startswith("!--"):
                self.warning("CommentAsSectionHeadingElementName")
            if sectionElementName and sectionElementName.startswith("!--"):
                self.warning("CommentAsSectionElementName")
            if headingElementName == "" and propName == "" and not isId and title != "-":
                self.warning("OmittedHeadingAndIdPropertyWithSectionElementName")

        return [title,isId,minPeriodFound,headingElementName,sectionElementName,propName,attributeDecorator]


    def parseTag(self,tag):
        tagName = ""
        idName = ""
        foundtagName = False
        classList = []
        # find extra attributes if there are any
        segments = tag.split("[")
        i = 0
        segment = segments[0]
        # find idname if there is any
        splitId = segment.split("#")
        if not foundtagName:
            tagFrag = splitId[0]
            foundtagName = True
            # classes can be right after the tagname
            splitClass = tagFrag.split(".")
            tagName = splitClass[0]
            if len(splitClass) > 1:
                classList += splitClass[1:]
        if len(splitId) > 1:
            idFrag = splitId[-1]
            # classes can also be after the idname
            splitClass = idFrag.split(".")
            idName = splitClass[0]
            if len(splitClass) > 1:
                classList += splitClass[1:]
        attrStrList = []
        if idName != "":
            attrStrList.append('id="'+idName+'"')
        if classList:
            attrStrList.append('class="'+(" ".join(classList)).strip()+'"')
        attrExtra = "]".join("[".join(tag.split("[")[1:]).split("]")[0:-1])
        if attrExtra != "":
            attrStrList.append(attrExtra)
        attributes = " ".join(attrStrList)

        if "<" in tagName or ">" in tagName:
            self.warning("AngleBracketInElementName")
        if "&" in tagName:
            self.warning("AmpersandInElementName")
        if tagName.startswith("/"):
            self.warning("LeadingForwardSlashInElementName")
        if len(tagName) > 1 and tagName.endswith("/"):
            self.warning("TrailingForwardSlashInElementName")
        if len(tagName) > 1 and tagName.startswith("!--"):
            self.warning("CommentAsElementName")
        return [tagName,attributes]

    def countIndents(self, line):
        spaces = 0
        for char in line:
            if char == " ":
                spaces+=1
            else:
                break
        return int(spaces / 2)  #hardcoded to 2 spaces per indent

    def isImplicitSectionClose(self):
        if self.isSectionClose() is False and self.ln.isThisSectionHeading and self.lenSectionStack and self.currSection:
            if self.currSection['sectionLvl'] >= self.memo(self.parseSection)[2]:
                return True
        return False

    def validateElementName(self, elementName):
        if not type(elementName) == type("") \
          or elementName.startswith("/") \
          or elementName.endswith("/") \
          or elementName.startswith("!--") \
          or "&" in elementName \
          or "<" in elementName \
          or ">" in elementName \
          or "[" in elementName \
          or "]" in elementName \
          or '"' in elementName \
          or "'" in elementName:
            return False
        return True

    def configMatterAndSource(self, source):
        spacing = {"*":list(" \t\n")}
        quoteSet = ['"',"'"]
        quoteGet = lambda: None
        source = source + "\n"

        def isStrSeqInData(data, seq, continueFor="", commentStart="", commentStop="", commentStartAfterStrNum=None, commentStopAfterStrNum=None):
            quoteGet = lambda: quoteCh
            portion = ""
            quoteCh = ""
            isCommentPossible = (not (commentStartAfterStrNum and commentStopAfterStrNum)) \
              and (commentStart and commentStop)
            commentOn = False
            commentPortion = ""
            countStrOfSeq = 0
            strSeq = seq[1:]
            strOfSeq = seq[0]
            found = 0
            for i,ch in enumerate(data):
                portion += ch
                normPortion = portion.lower()
                if strOfSeq == "":
                     strOfSeq, *strSeq = strSeq if len(strSeq) > 1 else [strSeq, ""]
                if type(strOfSeq) == type({}):                                          # e.g. {"*": True}
                    continueFor = list(strOfSeq.values())[0]
                    strOfSeq, *strSeq = strSeq if len(strSeq) > 1 else [strSeq, ""]
                if type(strOfSeq) == type(""):                                          # e.g. "interpretive"
                    strOfSeq = [strOfSeq]
                elif type(strOfSeq) == type(lambda: None):                              # quoteGet
                    strOfSeq = [quoteGet()]
                if type(continueFor) != type(True) and ch in continueFor \
                  and True not in [aStr.startswith(ch) for aStr in strOfSeq]:           # e.g list(" \t\n")
                    portion = ""
                    continue

                if commentStart and commentStop \
                  and not isCommentPossible and commentStartAfterStrNum == countStrOfSeq:
                    isCommentPossible = True
                elif commentStart and commentStop \
                  and isCommentPossible and commentStopAfterStrNum == countStrOfSeq:
                    isCommentPossible = False

                if isCommentPossible and data[:i+1].endswith(commentStart):
                    commentOn = True
                    commentPortion = ""
                    portion = ""
                    continue
                elif isCommentPossible and data[:i+1].endswith(commentStop):
                    commentOn = False
                    commentPortion = ""
                    portion = ""
                    continue
                elif commentOn:
                    portion = ""
                    continue

                if isCommentPossible \
                  and not commentOn and commentStart.startswith(commentPortion+ch):
                    commentPortion += ch
                elif isCommentPossible \
                  and commentOn and commentStop.startswith(commentPortion+ch):
                    commentPortion += ch

                if normPortion in strOfSeq:                                             # e.g. ['"',"'"]
                    if strSeq == [""]:
                        found = i
                        break
                    if strOfSeq == quoteSet:
                        quoteCh = normPortion
                    portion = ""
                    strOfSeq = ""
                    continueFor = ""
                    commentPortion = ""
                    countStrOfSeq += 1
                elif True in [aStr.startswith(normPortion) for aStr in strOfSeq]:
                    continue
                elif continueFor == True:
                    portion = ""
                    commentPortion = ""
                    continue
                else:
                    if isCommentPossible and not commentOn and commentStart.startswith(commentPortion):
                        pass
                    elif isCommentPossible and commentOn and commentStop.startswith(commentPortion):
                        pass
                    else:
                        break
            return found+1 if found > 0 else found

        doctype = ("<!doctype",spacing,"html",spacing,">")
        doctypeToDecl = (">",spacing,"<script")

        decl = ("<script",spacing,">",spacing,quoteSet,"interpretive",quoteGet,spacing,"</script>")
        declToStyl = ("</script>",spacing,"<style")

        styl = ("<style",spacing,">",{"*": True},"</style>")
        stylToInvok = ("</style>",spacing,"<script")

        declToInvok = ("</script>",spacing,"<script")

        invok = ("<script",spacing,"src=",quoteSet,{"*": True},quoteGet,spacing,">",{"*": True},"</script>")
        configMatter = ("api-version=",{"*": True},"\n===\n")

        isDoctypeInData = isStrSeqInData(source, doctype, continueFor=list(spacing.values())[0])
        isDoctypeToDeclComm = isStrSeqInData(source[isDoctypeInData-len(">"):], doctypeToDecl, \
          commentStart="<!--", \
          commentStop="-->", \
          commentStartAfterStrNum=1, \
          commentStopAfterStrNum=2 \
        )
        lenIfDoctypeToDeclComm = isDoctypeInData + isDoctypeToDeclComm-len(">")-len("<script") if isDoctypeToDeclComm else isDoctypeInData

        isDeclInData = isStrSeqInData(source[lenIfDoctypeToDeclComm:], decl, continueFor=list(spacing.values())[0])

        isDeclToStylComm = isStrSeqInData(source[lenIfDoctypeToDeclComm+isDeclInData-len("</script>"):], declToStyl, \
          commentStart="<!--", \
          commentStop="-->", \
          commentStartAfterStrNum=1, \
          commentStopAfterStrNum=2 \
        )
        lenIfDeclToStylComm = lenIfDoctypeToDeclComm+isDeclInData+isDeclToStylComm-len("</script>")-len("<style") if isDeclToStylComm else lenIfDoctypeToDeclComm+isDeclInData

        isStylInData = isStrSeqInData(source[lenIfDeclToStylComm:], styl, \
          continueFor=list(spacing.values())[0] \
        )

        isInvokBeforeStyl = isStrSeqInData(source[lenIfDoctypeToDeclComm+isDeclInData:], invok, continueFor=list(spacing.values())[0])
        if lenIfDeclToStylComm+isStylInData > isInvokBeforeStyl:
            isStylToInvok = 0
            isStylInData = 0
            isDeclToInvok = isStrSeqInData(source[lenIfDoctypeToDeclComm+isDeclInData-len("</script>"):], declToInvok, \
              commentStart="<!--", \
              commentStop="-->", \
              commentStartAfterStrNum=1, \
              commentStopAfterStrNum=2 \
            )
            lenIfStylToInvokComm = lenIfDoctypeToDeclComm+isDeclInData-len("</script>")+isDeclToInvok-len("<script")
        else:
            isStylToInvok = isStrSeqInData(source[lenIfDeclToStylComm+isStylInData-len("</style>"):], stylToInvok, \
              commentStart="<!--", \
              commentStop="-->", \
              commentStartAfterStrNum=1, \
              commentStopAfterStrNum=2 \
            )
            lenIfStylToInvokComm = lenIfDeclToStylComm+isStylInData+isStylToInvok-len("</style>")-len("<script") if isStylToInvok else lenIfDeclToStylComm+isStylInData

        isInvokInData = isStrSeqInData(source[lenIfStylToInvokComm:], invok, continueFor=list(spacing.values())[0])

        self.lenJsLn = 0
        if isDeclInData and isInvokInData:
            js = source[:lenIfStylToInvokComm+isInvokInData]
            self.lenJsLn = len(js.split("\n"))-1 if js else 0
            source = source[lenIfStylToInvokComm+isInvokInData:]
            sourceLines = source.split("\n")
            if sourceLines and sourceLines[0].strip() == "":
                self.lenJsLn += 1
                source = source[1:]


        isConfigMatterInData = isStrSeqInData(source, configMatter, continueFor=list(spacing.values())[0])

        configMatterStr = ""
        if isConfigMatterInData:
            configMatterStr = source[:isConfigMatterInData]
            source = source[isConfigMatterInData:]

        return {"configMatter": configMatterStr, "jsInterpDeclIndex": isDeclInData, "source": source}

    def applyConfigMatter(self, configMatterStr):
        verStart = configMatterStr.index("api-version=")
        verStop = configMatterStr[verStart:].index("\n")+verStart
        ver=configMatterStr[verStart+len("api-version="):verStop]

        lineNum = self.lenJsLn+len(configMatterStr[:verStart].split("\n"))
        largestVersionStr = None
        if "-" in ver:                                                         # -1, -0, 0.-1.0
            self.warning("NonStandardVersionString",lineNum=lineNum)
        else:
            try:
                largestVersionStr = self.largestVersionStr(self.api_version, ver)
            except ValueError:
                self.warning("NonStandardVersionString",lineNum=lineNum)

            if largestVersionStr == ver and largestVersionStr != self.api_version:
                self.warning("VersionStringTooLarge",lineNum=lineNum)

        configMatterLines = configMatterStr.split("\n")
        optStartLines = [line.lstrip().startswith("opt=") for line in configMatterLines]
        if True in optStartLines:
            lineIndex = optStartLines.index(True)
            colIndex = configMatterLines[lineIndex].index("opt=")+len("opt=")
            opt = "\n".join(configMatterLines[lineIndex:]).lstrip()[len("opt="):-len("\n===\n")]
            import json
            optObj = {}
            try:
                optObj = json.loads(opt)
            except json.JSONDecodeError as err:
                self.warning("ConfigForOptIsNotJSON", lineNum=self.lenJsLn+lineIndex+err.lineno, colNum=colIndex+err.colno, details=err.msg)
            self.opt.of = self.updatedObj(self.opt.of, optObj)

            originalOpt = self.Opt()
            for required in ['input','output','stderr']:
                originalRequired = originalOpt.of[required].keys()
                if (originalRequired):
                    k = list(originalRequired)[0]
                    try:
                        self.opt.of[required][k]
                    except Exception:                                   #KeyError if e.g. {}["input"][k], TypeError if e.g. {"input": ""}["input"][k]
                        self.opt.of[required] = originalOpt.of[required]
            try:
                self.opt.of['output']['baseIndent'] = int(self.opt.of['output']['baseIndent'])
            except Exception:
                self.opt.of['output']['baseIndent'] = originalOpt.of['output']['baseIndent']
            try:
                self.opt.of['stderr']['warnings']['verbosity'] = int(self.opt.of['stderr']['warnings']['verbosity'])
            except Exception:
                self.opt.of['stderr']['warnings']['verbosity'] = originalOpt.of['stderr']['warnings']['verbosity']
            try:
                if not self.validateElementName(self.opt.of['input']['defaultElementName']):
                    raise Exception
            except Exception:
                self.opt.of['input']['defaultElementName'] = originalOpt.of['input']['defaultElementName']


    def updatedObj(self, original, more):
        objN3 = deepcopy(original)
        for n,v in more.items():
            if n in objN3:
                if type(v) == type({}):
                    for _n,_v, in v.items():
                        if type(_v) == type({}):
                            for __n,__v in _v.items():
                                objN3[n][_n][__n] = __v
                        else:
                            objN3[n][_n] = _v
                else:
                  objN3[n] = v
        return objN3

    def warning(self, warningInfo, lineNum=None, colNum=0, details=None):
        toReturn = {
            "warningInfo": warningInfo,
            "lineNum": lineNum if lineNum is not None else self.lineNum,
            "colNum": colNum,
            "details": details,
        }
        self.warnings.append(toReturn)

    def outputFromWarnings(self, verbosity=None):
        warningText = ""
        if verbosity == None:
            verbosity = self.opt.of['stderr']['warnings']['verbosity']
        if verbosity >= 2:
            for i,(colNum, details, lineNum, warningInfo) in enumerate([self._.sortedDictValList(warning) for warning in self.warnings]):
                if warningInfo in self.warningDefs.messages:
                    messageId = warningInfo
                    typeId = self.warningDefs.messages[messageId]['type']
                    typeDescr = self.warningDefs.types[typeId]
                    message = self.warningDefs.messages[messageId]['message']
                else:
                    messageId = "Generic"
                    typeId = self.warningDefs._Undefined
                    typeDescr = self.warningDefs.types[typeId]
                    message = "Generic"
                if verbosity == 2:
                    warningStatement = (", " if i > 0 else "Warnings: ") + messageId+"/"+typeId+":"+str(lineNum)
                if verbosity >= 3:
                    warningStatement = "Warning, "
                    warningStatement += "line {}".format(lineNum)
                    if colNum:
                        warningStatement += ", column {}".format(colNum)
                    warningStatement += ": ("
                    warningStatement += str(messageId) + "/" + str(typeId)
                    warningStatement += ")"
                if verbosity >=4 and message:
                    warningStatement += "\n**" + (typeDescr + " " + message).lstrip() + "."
                    if details:
                        warningStatement += ' Reported as: "' + details + '".'
                if verbosity >= 5:
                    warningStatement += '\n>> ' + self.getLineFromLineNum(lineNum)
                    if colNum:
                        warningStatement += '\n' + ' '*(colNum+len(">> ")-1) + "^"
                if verbosity >= 3:
                    warningText += warningStatement + ("\n" if i < len(self.warnings)-1 else "")
                else:
                    warningText += warningStatement 
        elif verbosity == 1 and self.warnings:
            warningText = "Warnings: {}".format(len(self.warnings))
        return warningText

    def getLineFromLineNum(self, lineNum):
        if lineNum < (self.lenJsLn+self.lenConfigMatterLn):
            return self.configMatter.split("\n")[lineNum-self.lenJsLn-1]
        else:
            return self.lines[lineNum-self.lenJsLn-self.lenConfigMatterLn-1]

    def memo(self, func, l=None):
        if l is None:
            lineIndex = self.lineIndex
        else:
            lineIndex = l
        if lineIndex not in self.cache:
            self.cache[lineIndex] = {}
        if str(func) not in self.cache[lineIndex]:
            self.cache[lineIndex][str(func)] = func() if l is None else func(l)
        return self.cache[lineIndex][str(func)]

    largestVersionStr = lambda self,a,b: sorted([(".".join([format(int(n), \
          sorted([str(len(n)) for n in a.split(".")+b.split(".")])[-1]) \
          for n in v.split(".")]),v) \
          for v in (b, a)])[-1][1] # a, b reordered to return a if equivalent but not identical

    class _:
        sortedDict = lambda py35dict: sorted(py35dict.keys())
        sortedDictItemList = lambda py35dict: sorted(py35dict.items(), key=lambda tuple: tuple[0])
        sortedDictValList = lambda py35dict: [item[1] for item in sorted(py35dict.items(), key=lambda tuple: tuple[0])]
        uniqueList = lambda theList: [a for i,a in enumerate(theList) if theList.index(a) >= i] # to preserve order, not as set()
        isInRange = lambda theList, theIndex: len(theList)-1 >= theIndex
        getFlat = lambda theList: functools.reduce(lambda a, b: a + b, \
          [[e for e in theList if type(e) != type([])], \
          *[e for e in theList if type(e) == type([])]])
        rangeInclusive = lambda start, inclusiveStop: range(start, inclusiveStop+1)
        twoOf = lambda a,b: (a,b)
        noneOrPop = lambda theArr: theArr[-1] if theArr else None

        def printAndReturn(obj):
            print(obj)
            return obj

def main():
    p = ParserTriv()
    if len(sys.argv) > 1:
        if "--help" in sys.argv or "-h" in sys.argv:
            _help()
            exit()
        if "--dev-help" in sys.argv:
            _help(forDev=True)
            exit()
        if "--version" in sys.argv:
            print("Implementation version (PyRef3v)\n"+p.VERSION)
            exit()
        if "--api-version" in sys.argv:
            print(p.api_version)
            exit()
        if "--debug" in sys.argv:
            program.debug["FullTraceback"] = True
        if "--test" in sys.argv:
            verbose = "-v" in sys.argv or "--verbose" in sys.argv
            if verbose:
                if "--verbose" in sys.argv and "-v" in sys.argv:
                    _help(minimal=True, sysExit=program._sysExits["Usage"])
                if "--verbose" in sys.argv:
                    index = sys.argv.index("--verbose")
                if "-v" in sys.argv:
                    index = sys.argv.index("-v")
                if p._.isInRange(sys.argv,index+1) and sys.argv[index+1].isnumeric():
                    verbose = int(sys.argv[index+1])
                    if verbose < 0 or verbose > 5:
                        _help(minimal=True, sysExit=program._sysExits["Usage"])
                testSuite.config['verbosity'] = verbose
            if "--future" in sys.argv:
                testSuite.config['futureFeatures'] = True
            index = sys.argv.index("--test")
            if p._.isInRange(sys.argv,index+1) and sys.argv[index+1] == "--element":
                    testSuite.elementTest(verbose=verbose)
            elif p._.isInRange(sys.argv,index+1) and sys.argv[index+1] == "--document":
                limited = []
                ofVersionKnownGood = None
                if p._.isInRange(sys.argv,index+2):
                    if "." in sys.argv[index+2]:
                        ofVersionKnownGood = sys.argv[index+2]
                    elif re.fullmatch("(\d+[,-])*\d+",sys.argv[index+2]):
                        try:
                            limited = p._.getFlat([int(n) if n.isnumeric() else \
                              list(p._.rangeInclusive(*[int(s) for s in p._.twoOf(*n.split("-"))])) \
                              for n in sys.argv[index+2].split(",")])
                        except TypeError:   # 1,2-3-4,5
                            _help(minimal=True, sysExit=program._sysExits["Usage"])
                testSuite.documentTest(p, limited, ofVersionKnownGood)
            else:
                if not program.debug["TestNum"]:
                    testSuite.elementTest(verbose=verbose)
                testSuite.documentTest(p)
            exit()
        else:
            verbose = "-v" in sys.argv or "--verbose" in sys.argv
            if verbose:
                if "--verbose" in sys.argv and "-v" in sys.argv:
                    _help(minimal=True, sysExit=program._sysExits["Usage"])
                if "--verbose" in sys.argv:
                    index = sys.argv.index("--verbose")
                if "-v" in sys.argv:
                    index = sys.argv.index("-v")
                if p._.isInRange(sys.argv,index+1) and sys.argv[index+1].isnumeric():
                    verbose = int(sys.argv[index+1])
                    if verbose < 0 or verbose > 5:
                        _help(minimal=True, sysExit=program._sysExits["Usage"])
                p.opt.of['stderr']['warnings']['verbosity'] = verbose
    filename = _initFalse
    if len(sys.argv) > 1 and sys.stdin.isatty():
            filename = sys.argv[-1]
            try:
                with open(filename) as f:
                    filedata = f.read()
            except BaseException as exception:
                sysExit, message = program._theExits(exception, program._mainExits, "IOERR", ' while reading "'+filename+'"')
                print(message, file=sys.stderr)
                if program._isDebug(sysExit):
                    if p.warnings: print(p.outputFromWarnings(verbosity=4), file=sys.stderr)
                    raise exception
    elif not sys.stdin.isatty():
        filename = None
        try:
            filedata = sys.stdin.read()
        except BaseException as exception:
            sysExit, message = program._theExits(exception, program._mainExits, "IOERR", ' while reading standard input')
            print(message, file=sys.stderr)
            if program._isDebug(sysExit):
                if p.warnings: print(p.outputFromWarnings(verbosity=4), file=sys.stderr)
                raise exception
    else:
        _help(minimal=True, sysExit=0)    

    try:
        print(p.compile(filedata))
    except BaseException as exception:
        sysExit, message = program._theExits(exception, program._mainExits, "SOFTWARE", ' while processing '+('"'+filename+'"' if filename else 'standard input'))
        print(message, file=sys.stderr)
        if program._isDebug(sysExit):
            if p.warnings: print(p.outputFromWarnings(verbosity=4), file=sys.stderr)
            raise exception

    isOutputFromWarnings = p.outputFromWarnings()
    if isOutputFromWarnings:
        print(isOutputFromWarnings, file=sys.stderr)
    exit(program._sysExits["_WARNINGS"] if p.warnings else 0)


def _help(minimal=False, forDev=False, sysExit=None):
    import os
    progName = (os.path.basename(sys.argv[0]))
    print("Usage: "+progName+" [OPTION] FILE")
    if minimal:
        print("Try '"+progName+" --help' for more information.")
    elif not forDev:
        print("\n"+"""
OPTION:
  -v, --verbose  Sets verbosity to 1
    VERBOSITY:   Sets verbosity between 0 and 5
      0          Does not display warnings
      1          Displays an aggregate count of warnings
      2          Displays a string of each warning id and position
      3          Displays the warning id and type per line
      4          Also displays full warnings per line
      5          Also displays line content

  --version      Displays the implementation version number
  --api-version  Displays the API version number
  --dev-help     Displays help information for developers
  --help         Displays this help information
        """.strip())
    elif forDev:
        #print"#"*80)
        print("   or: "+("python3 "+sys.argv[0] if sys.argv[0].endswith(".py") else sys.argv[0]) + " [--test [TESTS] [--verbose [VERBOSITY]] [TEST_OPT]]")
        print("\n"+"""
  --test         Runs self tests

TESTS:
  --element      Only runs element matching tests
  --document     Only runs document tests
      TEST_NUM   Only runs document tests in range,
                 e.g. 1,2,3-6,7
                   or of a specific version,
                 e.g. 0.50.0
  -v, --verbose  Sets test verbosity to 1
    VERBOSITY:   Sets test verbosity between 0 and 5
      0          Only displays failing items
      1          Also displays an aggregate count of passing and failing items
      2          Displays passing items and details of failing items
      3          Displays details of passing and failing items
      4          Also displays returned results for passing items
      5          Also displays the first found not expected line for failing items

TEST_OPT:
  --future       Enables tests outside current version

OPTION:
  --debug        Enables full traceback output for internal exceptions
        """[1:].rstrip())
    exit(sysExit)

if __name__=="__main__":
    main()
