paddingExamples = [
("""
< Test blankline b/w statements
outer1:
  inner1:
    content

outer2:
  inner2:
    content
""",
"0.13.1"),
("""
< Test 2 blanklines b/w statements
outer1:
  inner1:
    content


outer2:
  inner2:
    content
""",
"0.13.1"),
("""
< Test combined padding & blankline
outer1:

  padded1:
    content

outer2:
  inner2:
    content
""",
"0.13.1"),
("""
< Test combined padding&blankline, + extra blankline
outer1:

  padded1:
    content


outer2:
  inner2:
    content
""",
"0.13.1"),
("""
< Test leading blankline
outer1:


  inner1:
    content
outer2:
  inner2:
    content
""",
"0.13.1"),
# < Test #2 leading blankline
("""outer1:


  inner1:
    content
root content
""",
"0.13.1"),
("""
< Test 2-line padding
outer:


  inner1:
    content


  inner2:
    content
""",
"0.13.1"),
("""
< Test blankline + 1-line padding
outer:


    inner:
      content

    inner:
      content

next:
""",
"0.13.1"),
("""
< Test 1-line padding + blankline
outer:

  inner1:
    content


  inner2:
    content
""",
"0.13.1"),
("""
< Test 1-line padding
outer:
  mid:

    inner1:
      content

    inner2:
      content
""",
"0.13.1"),
("""
< Test x-line blanklines
outer:

  inner1:
    content

  inner2:
    content

  inner3:
    content



blah:
""",
"0.13.1"),
("""
< Test x-line blanklines
outer:



  inner1:
    content

  inner2:
    content

  inner3:
    content



next:
""",
"0.13.1"),
("""
< Test multi-level mismatch
outer:


    mid1:



      inner1:
        content

      inner2:
        content

      inner3:
        content


next:
""",
"0.13.1"),
("""
< Test a bunch of placed etc
outer:
  mid:
    inner:
      innie:
        inniest:
          content

next:
  nextinner:
    content
""",
"0.13.1"),
("""
< No blanklines
first:
  content
second:
  content
""",
"0.13.1"),
("""
< Test last line etc
first:
  content1

  content2


  content3



  content4""",
"0.13.1"),
("""
< Leading newlines and indentation in content

a1:


  b:

    c:
      content
      extra line of content
        indented line in content

          indented line with leading newline in content

a2:

  more content


  b:

    extra content

a3:
  also content
""",
"0.13.1"),
("""
outer:
  mid1:mid2:
    inner:
      content
""",
"0.13.1"),
("""outer:mid:
  inner:
    content""",
"0.13.1"),
("""
a:
  b::
""",
"0.13.1"),
("""
simple:
""",
"0.13.1"),
("""
a:
  b:
    content, line 1
      indented content, line 2
""",
"0.13.1"),
("""
  test:
    test2:
      !!!
test
      !!!
""",
"0.13.1"),
("""
< Full self-closing element
a:

  b[]//
""",
"0.18.1"),
("""
< Full self-closing element with attributes
a:
  b.a.b#c[abc="123" def="456"]:
    c:
      d.a.b.c#d[abc="123" def="456"]//
""",
"0.18.1"),
("""
< Void self-closing element
a:

  b[]/
""",
"0.21.4"),
("""
a| b
""",
"0.21.1"),
("""
a|
  b
""",
"0.21.1"),
("""
a|b|c| d
""",
"0.21.1"),
("""
a|
  b|
    c|
      d
""",
"0.21.1"),
("""
a:b| c
""",
"0.21.1"),
("""
a|b[]/
""",
"0.21.1"),
("""
a:b|c:
""",
"0.21.1"),
("""
a:b|c:d|
""",
"0.21.1"),
("""
< Ambiguity between content and attribute resolved by parsing from left
a[b]: c[]:
""",
"0.13.1"),
]

paddingExpectedResults = [
'''
<!-- Test blankline b/w statements -->
<outer1>
  <inner1>
    content
  </inner1>
</outer1>

<outer2>
  <inner2>
    content
  </inner2>
</outer2>
''',
'''
<!-- Test 2 blanklines b/w statements -->
<outer1>
  <inner1>
    content
  </inner1>
</outer1>


<outer2>
  <inner2>
    content
  </inner2>
</outer2>
''',
'''
<!-- Test combined padding & blankline -->
<outer1>

  <padded1>
    content
  </padded1>

</outer1>

<outer2>
  <inner2>
    content
  </inner2>
</outer2>
''',
'''
<!-- Test combined padding&blankline, + extra blankline -->
<outer1>

  <padded1>
    content
  </padded1>

</outer1>


<outer2>
  <inner2>
    content
  </inner2>
</outer2>
''',
'''
<!-- Test leading blankline -->
<outer1>


  <inner1>
    content
  </inner1>
</outer1>
<outer2>
  <inner2>
    content
  </inner2>
</outer2>
''',
'''
<outer1>


  <inner1>
    content
  </inner1>
</outer1>
root content
''',
'''
<!-- Test 2-line padding -->
<outer>


  <inner1>
    content
  </inner1>


  <inner2>
    content
  </inner2>


</outer>
''',
'''
<!-- Test blankline + 1-line padding -->
<outer>


    <inner>
      content
    </inner>

    <inner>
      content
    </inner>

</outer>

<next></next>
''',
'''
<!-- Test 1-line padding + blankline -->
<outer>

  <inner1>
    content
  </inner1>


  <inner2>
    content
  </inner2>

</outer>
''',
'''
<!-- Test 1-line padding -->
<outer>
  <mid>

    <inner1>
      content
    </inner1>

    <inner2>
      content
    </inner2>

  </mid>
</outer>
''',
'''
<!-- Test x-line blanklines -->
<outer>

  <inner1>
    content
  </inner1>

  <inner2>
    content
  </inner2>

  <inner3>
    content
  </inner3>

</outer>



<blah></blah>
''',
'''
<!-- Test x-line blanklines -->
<outer>



  <inner1>
    content
  </inner1>

  <inner2>
    content
  </inner2>

  <inner3>
    content
  </inner3>



</outer>



<next></next>
''',
'''
<!-- Test multi-level mismatch -->
<outer>


    <mid1>



      <inner1>
        content
      </inner1>

      <inner2>
        content
      </inner2>

      <inner3>
        content
      </inner3>


    </mid1>


</outer>


<next></next>
''',
'''
<!-- Test a bunch of placed etc -->
<outer>
  <mid>
    <inner>
      <innie>
        <inniest>
          content
        </inniest>
      </innie>
    </inner>
  </mid>
</outer>

<next>
  <nextinner>
    content
  </nextinner>
</next>
''',
'''
<!-- No blanklines -->
<first>
  content
</first>
<second>
  content
</second>
''',
'''
<!-- Test last line etc -->
<first>
  content1

  content2


  content3



  content4
</first>
''',
'''
<!-- Leading newlines and indentation in content -->

<a1>


  <b>

    <c>
      content
      extra line of content
        indented line in content

          indented line with leading newline in content
    </c>

  </b>

</a1>

<a2>

  more content


  <b>

    extra content

  </b>

</a2>

<a3>
  also content
</a3>
''',
'''
<outer>
  <mid1><mid2>
    <inner>
      content
    </inner>
  </mid2></mid1>
</outer>
''',
'''
<outer><mid>
  <inner>
    content
  </inner>
</mid></outer>
''',
'''
<a>
  <b><div></div></b>
</a>
''',
'''
<simple></simple>
''',
'''
<a>
  <b>
    content, line 1
      indented content, line 2
  </b>
</a>
''',
'''
  <test>
    <test2>
      <!--
test
      -->
    </test2>
  </test>
''',
'''
<!-- Full self-closing element -->
<a>

  <b/>

</a>
''',
'''
<!-- Full self-closing element with attributes -->
<a>
  <b id="c" class="a b" abc="123" def="456">
    <c>
      <d id="d" class="a b c" abc="123" def="456"/>
    </c>
  </b>
</a>
''',
'''
<!-- Void self-closing element -->
<a>

  <b>

</a>
''',
'''
<a>b</a>
''',
'''
<a>
  b
</a>
''',
'''
<a><b><c>d</c></b></a>
''',
'''
<a>
  <b>
    <c>
      d
    </c>
  </b>
</a>
''',
'''
<a:b>c</a:b>
''',
'''
<a><b></a>
''',
'''
<a><b|c></b|c></a>
''',
'''
<a:b><c:d></c:d></a:b>
''',
'''
<!-- Ambiguity between content and attribute resolved by parsing from left -->
<a b>c[]:</a>
'''
]

sectionExamples = [
("""
< Test single section with content
[Section]
test
[]
""",
"0.13.1"),
("""
< Test single section with left-justified and non-justified content
[Section]
a1:
  \'\'\'
content
left justified
\'\'\'
a2:
  \"\"\"
  test
non-justified
  \"\"\"
[]
""",
"0.13.1"),
("""
[Outer]
[.Mid1.]
[..Inner1-1..]
content 1-1
[..Inner1-2..]
content 1-2
[]
[.Mid2.]
[..Inner2-1..]
content 2-1
[..Inner2-2..]
'''
content 2-2
'''
[[[]]]
""",
"0.13.1"),
("""
[Top]
[.Middle1.]
[..Lowest..]
[.Middle2.]
""",
"0.13.1"),
("""
      [Top]
    [.Middle1.]
  [..Lowest..]
    [.Middle2.]
""",
"0.13.1"),
("""
this:
[under_this]
content
[]
[under_this2]
""",
"0.13.1"),
("""
this:
[under_this1]

content

[]

[under_this2]
""",
"0.35.0"),
("""
this:
  [under_this]
  content
  []
[under_this]
""",
"0.13.1"),
("""
this:
  [under_this1]
  content
  []

[under_this2]
""",
"0.35.0"),
("""
outer:
[section]
inner:
  content
""",
"0.13.1"),
("""
[[[Section1]]]
[[Section2]]
[Section3]
[.Section4.]
[..Section5..]
""",
"0.13.1"),
("""
< Decorator Tests
[Sec 1]
=h1/div
[Sec 2]#
=/div id        <!-- underscore spaces -->
[Sec 3]/section
=/section
[Sec 4]#/section
=/section id    <!-- underscore spaces -->
[Sec 4]h2
=h2/div
[Sec 5]#h2
=h2/div id      <!-- underscore spaces -->
[Sec 6]h2/section
=h2/section
[Sec 7]#h2/section
=h2/section id  <!-- underscore spaces -->
[Sec 8]/section name
=/section name
[Sec 9]h2/section name
=h2/section name
[Sec 10]#h2/section myId
=h2/section myId <!-- underscore spaces -->
""",
"0.45.8"),
("""
< indented element is placed in the outer element after section close
outer:
  [Inner1]/inner1
  content
  []
  inner2:
    content
""",
"0.45.8"),
("""
< footer is placed in the two outer elements after section close
html:
  body:
[Section]
content
[]
    footer: etc
""",
"0.13.1"),
("""
< Sections will add extra indentation to your quoted literal content for clarity,
< but when this is not desired, like in preformatted text,
< you may omit indentation from the trailing quote toggle,
< to produce left-justified sectioned quoted content
[[Body]]
[Section]
element:
  content that will be output with 3 indents for clarity

element:
  '''
  content that will also be output with 3 indents for clarity
  '''

pre:
  '''
  content that will be output with only the 1 indent as per input
'''

pre:
  '''
content that will be output with no indents as per input
'''
""",
"0.13.1"),
("""
< Section reset
[[[Section 1]]]
[[Section 2]]
[Section 3]
content in sections
[]*
content outside of sections
""",
"0.17.1"),
("""
a:
[[[[B]]]]
[[[C]]]
[]
c2:
  n
""",
"0.11.6"),
("""
r:
[R]
r:
[.r.]
[]*
[.R.]
r:
""",
"0.24.6"),
("""
a:
[B]
""",
"0.24.7"),
("""
[aaa]#:
""",
"0.29.0"),
("""
[A &amp; B & C]
[&A &amp; B & C]
[A & B &amp; C]
[A & B &amp; C&]
[A &ndash; B & C]
""",
"0.29.2"),
("""
api-version=0
opt={"input":{"AngleBracketInSectionTitle":true}}
===
[<i>A B C]#
[A <i>B C]#
[A <i>B</i> C]#
[A B C<i>]#
[A>B]#
""",
"0.45.0"),
("""
[A>B]
[A<B>C]
""",
"0.29.2"),
("""
[A]# & &
[A]b & &
[A] & & &
""",
"0.29.9"),
("""
[A] & //
""",
"0.36.2"),
("""
[A] & <
[A] & >
""",
"0.29.9.0.1"),
("""
[A] & "[]"
[A] & []
""",
"0.29.9.0.1"),
("""
[[[A&A]]] & ]&
[[[A&A]] & ]&
""",
"0.29.9.0.1"),
("""
[A]&a aaa
""",
"0.29.9.0.1"),
("""
[A] & "<"
[A] & "'<'"
[A] & '"<"'
[A] & ""'"<"'
[A] & '''"<"'
[A] & "'"'<'
[A] & "'<"
""",
"0.29.9.0.2"),
("""
[A] & "'<'
""",
"0.29.9.0.2"),
("""
[A] & ""'"<"
""",
"0.29.9.0.2"),
('''
[A] & '"""<"
''',
"0.29.9.0.2"),
("""
[A] & ""'<'"
""",
"0.29.9.0.2"),
("""
[A] & '"'<'"'
""",
"0.29.9.0.2"),
("""
[A] & "'"'"'<"'"'"'
""",
"0.29.9.0.2"),
("""
[A] & '"'<"'
""",
"0.29.9.0.2"),
("""
[A] & "''<''
""",
"0.29.9.0.2"),
("""
[A] & ""<
""",
"0.29.9.0.2"),
("""
[A] & ""''<
""",
"0.29.9.0.2"),
("""
[A] & "<
""",
"0.29.9.0.2"),
("""
[A] & ""'<
""",
"0.29.9.0.2"),
("""
[A] & "<" < "<"
""",
"0.29.9.0.2"),
("""
[A] &
""",
"0.29.2"),
("""
[A] b  id aaa
""",
"0.34.4"),
("""
a:
  b: n
[B]
""",
"0.35.0"),
("""
a:
  b[]//
[B]
""",
"0.35.0"),
("""
a:
  b:
    n
[B]
""",
"0.35.0"),
("""
a:
  b: !!!
bbb
!!!
[C]
""",
"0.35.0"),
("""
a:
  b:
    !!!
    bbb
!!!
[C]
""",
"0.35.0"),
("""
a:
  b:
    < bbb
[C]
""",
"0.35.0"),
("""
a:
  b:
    '''
    '''
[B]
""",
"0.35.0"),
("""
a:
[B1]
[]
  < bbb
[B2]
[]
""",
"0.35.0"),
("""
a:
[B1]
[]
  !!!
bbb
!!!
[B2]
[]
""",
"0.35.0"),
("""
a:
[B]
[]
  '''
bbb
'''
[A]
[]
""",
"0.10.0"),
("""
[]*
""",
"0.40.2"),
("""
["A"]#
""",
"0.29.2"),
("""
['A']#
""",
"0.10.1"),
("""
["'A'"]#
""",
"0.41.2"),
("""
api-version=0
opt={"input":{"AngleBracketInSectionTitle":true}}
===
[<a></a>]#
""",
"0.45.0"),
("""
api-version=0
opt={"output": {"baseIndent": 1}}
===
[A]
b:
  '''
n
'''
""",
"0.45.0"),
("""
[ ]
[\t]
""",
"0.42.0"),
("""
[A] 
    < space character
""",
"0.45.5"),
("""
[A]!--
[A]h1/!--
""",
"0.45.8"),
("""
[[]
""",
"0.47.5"),
("""
[]]
""",
"0.47.5"),
("""
[[[]]
""",
"0.47.5"),
("""
[[]]]
""",
"0.47.5"),
]
sectionExpectedResults = [
"""
<!-- Test single section with content -->
<div><h1>Section</h1>
  test
</div>
""",
"""
<!-- Test single section with left-justified and non-justified content -->
<div><h1>Section</h1>
  <a1>
content
left justified
  </a1>
  <a2>
    test
  non-justified
  </a2>
</div>
""",
"""
<div><h1>Outer</h1>
  <div><h1>Mid1</h1>
    <div><h1>Inner1-1</h1>
      content 1-1
    </div>
    <div><h1>Inner1-2</h1>
      content 1-2
    </div>
  </div>
  <div><h1>Mid2</h1>
    <div><h1>Inner2-1</h1>
      content 2-1
    </div>
    <div><h1>Inner2-2</h1>
content 2-2
    </div>
  </div>
</div>
""",
"""
<div><h1>Top</h1>
  <div><h1>Middle1</h1>
    <div><h1>Lowest</h1>
    </div>
  </div>
  <div><h1>Middle2</h1>
  </div>
</div>
""",
"""
      <div><h1>Top</h1>
      <div><h1>Middle1</h1>
      <div><h1>Lowest</h1>
      </div>
      </div>
      <div><h1>Middle2</h1>
      </div>
      </div>
""",
"""
<this>
<div><h1>under_this</h1>
  content
</div>
<div><h1>under_this2</h1>
</div>
</this>
""",
"""
<this>
<div><h1>under_this1</h1>

  content

</div>

<div><h1>under_this2</h1>
</div>
</this>
""",
"""
<this>
  <div><h1>under_this</h1>
    content
  </div>
<div><h1>under_this</h1>
</div>
</this>
""",
"""
<this>
  <div><h1>under_this1</h1>
    content
  </div>

<div><h1>under_this2</h1>
</div>
</this>
""",
"""
<outer>
<div><h1>section</h1>
  <inner>
    content
  </inner>
</div>
</outer>
""",
"""
<div><h1>Section1</h1>
  <div><h1>Section2</h1>
    <div><h1>Section3</h1>
      <div><h1>Section4</h1>
        <div><h1>Section5</h1>
        </div>
      </div>
    </div>
  </div>
</div>
""",
('''
<!-- Decorator Tests -->
<div><h1>Sec 1</h1>
  =h1/div
</div>
<div id="Sec_2">
  =/div id        <!-- underscore spaces -->
</div>
<section>
  =/section
</section>
<section id="Sec_4">
  =/section id    <!-- underscore spaces -->
</section>
<div><h2>Sec 4</h2>
  =h2/div
</div>
<div id="Sec_5"><h2>Sec 5</h2>
  =h2/div id      <!-- underscore spaces -->
</div>
<section><h2>Sec 6</h2>
  =h2/section
</section>
<section id="Sec_7"><h2>Sec 7</h2>
  =h2/section id  <!-- underscore spaces -->
</section>
<section name="Sec 8">
  =/section name
</section>
<section name="Sec 9"><h2>Sec 9</h2>
  =h2/section name
</section>
<section myId="Sec_10"><h2>Sec 10</h2>
  =h2/section myId <!-- underscore spaces -->
</section>
''',
'OmittedHeadingAndIdPropertyWithSectionElementName<6:0>'),
('''
<!-- indented element is placed in the outer element after section close -->
<outer>
  <inner1>
    content
  </inner1>
  <inner2>
    content
  </inner2>
</outer>
''',
'OmittedHeadingAndIdPropertyWithSectionElementName<3:0>'),
"""
<!-- footer is placed in the two outer elements after section close -->
<html>
  <body>
<div><h1>Section</h1>
  content
</div>
    <footer>etc</footer>
  </body>
</html>
""",
"""
<!-- Sections will add extra indentation to your quoted literal content for clarity, -->
<!-- but when this is not desired, like in preformatted text, -->
<!-- you may omit indentation from the trailing quote toggle, -->
<!-- to produce left-justified sectioned quoted content -->
<div><h1>Body</h1>
  <div><h1>Section</h1>
    <element>
      content that will be output with 3 indents for clarity
    </element>

    <element>
  content that will also be output with 3 indents for clarity
    </element>

    <pre>
  content that will be output with only the 1 indent as per input
    </pre>

    <pre>
content that will be output with no indents as per input
    </pre>
  </div>
</div>
""",
"""
<!-- Section reset -->
<div><h1>Section 1</h1>
  <div><h1>Section 2</h1>
    <div><h1>Section 3</h1>
      content in sections
    </div>
  </div>
</div>
content outside of sections
""",
"""
<a>
<div><h1>B</h1>
  <div><h1>C</h1>
  </div>
  <c2>
    n
  </c2>
</div>
</a>
""",
"""
<r>
<div><h1>R</h1>
  <r></r>
  <div><h1>r</h1>
  </div>
</div>
<div><h1>R</h1>
  <r></r>
</div>
</r>
""",
"""
<a>
<div><h1>B</h1>
</div>
</a>
""",
"""
<div aaa #></div>
""",
'''
<div><h1>A &amp; B &amp; C</h1>
</div>
<div><h1>&amp;A &amp; B &amp; C</h1>
</div>
<div><h1>A &amp; B &amp; C</h1>
</div>
<div><h1>A &amp; B &amp; C&amp;</h1>
</div>
<div><h1>A &ndash; B &amp; C</h1>
</div>
''',
'''
<div id="A_B_C">
</div>
<div id="A_B_C">
</div>
<div id="A_B_C">
</div>
<div id="A_B_C">
</div>
<div id="A>B">
</div>
''',
'''
<div><h1>A&gt;B</h1>
</div>
<div><h1>A&lt;B&gt;C</h1>
</div>
''',
('''
<div id="A" &>
</div>
<div &><b>A</b>
</div>
<div & &><h1>A</h1>
</div>
''',
'UnquotedAmpersandInAttributeDecorator<1:0>, UnquotedAmpersandInAttributeDecorator<2:0>, UnquotedAmpersandInAttributeDecorator<3:0>'),
('''
<div //><h1>A</h1>
</div>
''',
'TrailingForwardSlashInAttributeDecorator<1:0>'),
('''
<div <><h1>A</h1>
</div>
<div >><h1>A</h1>
</div>
''',
'UnquotedAngleBracketInAttributeDecorator<1:0>, UnquotedAngleBracketInAttributeDecorator<2:0>'),
'''
<div "[]"><h1>A</h1>
</div>
<div []><h1>A</h1>
</div>
''',
('''
<div ]&><h1>A&amp;A</h1>
  [[[A&A]] & ]&
</div>
''',
'UnquotedAmpersandInAttributeDecorator<1:0>, SquareBracketInSectionTitle<2:0>'),
'''
<div a aaa><h1>A</h1>
</div>
''',
"""
<div "<"><h1>A</h1>
</div>
<div "'<'"><h1>A</h1>
</div>
<div '"<"'><h1>A</h1>
</div>
<div ""'"<"'><h1>A</h1>
</div>
<div '''"<"'><h1>A</h1>
</div>
<div "'"'<'><h1>A</h1>
</div>
<div "'<"><h1>A</h1>
</div>
""",
('''
<div "'<'><h1>A</h1>
</div>
''',
'NonMatchingQuoteInAttributeDecorator<1:0>'),
('''
<div ""'"<"><h1>A</h1>
</div>
''',
'NonMatchingQuoteInAttributeDecorator<1:0>'),
('''
<div '"""<"><h1>A</h1>
</div>
''',
'NonMatchingQuoteInAttributeDecorator<1:0>'),
('''
<div ""'<'"><h1>A</h1>
</div>
''',
'NonMatchingQuoteInAttributeDecorator<1:0>'),
('''
<div '"'<'"'><h1>A</h1>
</div>
''',
'UnquotedAngleBracketInAttributeDecorator<1:0>'),
('''
<div "'"'"'<"'"'"'><h1>A</h1>
</div>
''',
'UnquotedAngleBracketInAttributeDecorator<1:0>'),
('''
<div '"'<"'><h1>A</h1>
</div>
''',
'NonMatchingQuoteInAttributeDecorator<1:0>'),
('''
<div "''<''><h1>A</h1>
</div>
''',
'NonMatchingQuoteInAttributeDecorator<1:0>'),
('''
<div ""<><h1>A</h1>
</div>
''',
'UnquotedAngleBracketInAttributeDecorator<1:0>'),
('''
<div ""''<><h1>A</h1>
</div>
''',
'UnquotedAngleBracketInAttributeDecorator<1:0>'),
('''
<div "<><h1>A</h1>
</div>
''',
'NonMatchingQuoteInAttributeDecorator<1:0>'),
('''
<div ""'<><h1>A</h1>
</div>
''',
'NonMatchingQuoteInAttributeDecorator<1:0>'),
('''
<div "<" < "<"><h1>A</h1>
</div>
''',
'UnquotedAngleBracketInAttributeDecorator<1:0>'),
'''
<div><h1>A</h1>
</div>
''',
'''
<div  id="A" aaa><b>A</b>
</div>
''',
'''
<a>
  <b>n</b>
<div><h1>B</h1>
</div>
</a>
''',
'''
<a>
  <b/>
<div><h1>B</h1>
</div>
</a>
''',
'''
<a>
  <b>
    n
  </b>
<div><h1>B</h1>
</div>
</a>
''',
'''
<a>
  <b><!-- bbb -->
<div><h1>C</h1>
</div>
  </b>
</a>
''',
'''
<a>
  <b>
    <!--
    bbb
    -->
<div><h1>C</h1>
</div>
  </b>
</a>
''',
'''
<a>
  <b>
    <!-- bbb -->
<div><h1>C</h1>
</div>
  </b>
</a>
''',
'''
<a>
  <b>
  </b>
<div><h1>B</h1>
</div>
</a>
''',
'''
<a>
<div><h1>B1</h1>
</div>
  <!-- bbb -->
<div><h1>B2</h1>
</div>
</a>
''',
'''
<a>
<div><h1>B1</h1>
</div>
  <!--
bbb
  -->
<div><h1>B2</h1>
</div>
</a>
''',
'''
<a>
<div><h1>B</h1>
</div>
bbb
</a>
<div><h1>A</h1>
</div>
''',
'''
''',
'''
<div id='"A"'>
</div>
''',
'''
<div id="'A'">
</div>
''',
('''
<div id="`'A'`">
</div>
''',
'SingleAndDoubleQuoteInSectionIdOrTitlePropertyValue<1:0>'),
'''
<div id="">
</div>
''',
'''
  <div><h1>A</h1>
    <b>
n
    </b>
  </div>
''',
'''
[ ]
[\t]
''',
'''
<div><h1>A</h1>
      <!-- space character -->
</div>
''',
('''
<div><!-->A</!-->
</div>
<!--><h1>A</h1>
</!-->
''',
'CommentAsSectionHeadingElementName<1:0>, CommentAsSectionElementName<2:0>'),
("""
[[]
""",
"SquareBracketInSectionTitle<1:0>"),
("""
[]]
""",
"SquareBracketInSectionTitle<1:0>"),
("""
[[[]]
""",
"SquareBracketInSectionTitle<1:0>"),
("""
[[]]]
""",
"SquareBracketInSectionTitle<1:0>"),
]

quoteExamples = [
("""
< Test mixed quotes
'''
```
\"\"\"
!!!
  triple-single-quoted block
  can print triple double-quotes + backticks
!!!
\"\"\"
```
'''

\"\"\"
```
'''
!!!
  triple-double-quoted block
  can print triple single-quotes + backticks
!!!
```
'''
\"\"\"

```
'''
\"\"\"
!!!
  triple-backtick-quoted block
  can print both triple quotes + un-escaped <html>
!!!
\"\"\"
'''
```

!!!
\"\"\"
'''
```
  commented block
  can print all triple quotes
```
'''
\"\"\"
!!!

'''
extra content
'''
""",
"0.13.1"),
("""
a[a attr]:
  b[b attr]:
    c[c attr]:
      content
""",
"0.13.1"),
("""
:
  '''

  '''
""",
"0.13.1"),
("""
section:
  block:
    line:flex:
      nav: A1
      aside: A2

section:
  block:
    line:flex: randomtext
      nav: A1
      aside: A2

section:
  block:
    line:title: A1
    line:date: A2
""",
"0.13.1"),
("""
a:
  '''
  '''
""",
"0.10.1"),
("""
a:
  b:
[C]
d: '''
n
'''
""",
"0.27.2"),
("""
a:
  b: '''
n
n
n
'''
""",
"0.43.0"),
("""
a:
  !!!
  !!!
""",
"0.10.1"),
("""
a:
  b:
[C]
d: '''
n
n
n
'''
""",
"0.43.0"),
("""
a:
  b:
[C]
d: '''
n
n
n
   '''
""",
"0.43.0"),
("""
a:
  '''
""",
"0.24.1"),
("""
a:
  !!!
""",
"0.24.1"),
("""
< Should not pass - meant for testing the test framework
a
""",
"0.9999"),
("""
a: '''

'''
""",
"0.27.0"),
("""
a:
  '''

'''
""",
"0.10.1"),
("""
a: '''


'''
""",
"0.27.0"),
("""
a:
  '''


'''
""",
"0.10.1"),
("""
a: '''
n
'''
""",
"0.27.0"),
("""
a:
  '''
n
'''
""",
"0.10.1"),
("""
a: '''

n

'''
""",
"0.27.0"),
("""
a:
  '''

n

'''
""",
"0.10.1"),
("""
a: !!!

!!!
""",
"0.27.2"),
("""
a:
  !!!

  !!!
""",
"0.10.1"),
("""
a: !!!


!!!
""",
"0.27.2"),
("""
a:
  !!!


!!!
""",
"0.10.1"),
("""
a: !!!
n
!!!
""",
"0.27.2"),
("""
a:
  !!!
n
!!!
""",
"0.10.1"),
("""
a: !!!

n

!!!
""",
"0.27.2"),
("""
a:
  !!!

n

!!!
""",
"0.10.1"),
("""
a: '''
'''
""",
"0.27.2"),
("""
a: !!!
!!!
""",
"0.27.2"),
("""
a:
  b:
[C]
d:
  '''
n
n
n
  '''
""",
"0.10.1"),
("""
< *
a:
  b:
[C]
d:
  '''
n
n
n
'''
""",
"0.10.1"),
("""
a:
  b:
[C]
d:
  '''
  n
  '''
""",
"0.10.1"),
("""
a:
  b:
[C]
d:
  '''
  n
'''
""",
"0.10.1"),
("""
a:
  b:
[C]
d: '''
n
   '''
""",
"0.27.2"),
("""
!a:
""",
"0.29.0"),
("""
!a:
  ?b:
    @c:
""",
"0.29.0"),
("""
!a?:
""",
"0.36.1"),
("""
!a[]?//
""",
"0.39.3"),
("""
!a[a]?//
""",
"0.29.0"),
("""
!a[a="a"]?//
""",
"0.29.0"),
("""
!a[a="a"]?:
""",
"0.29.0"),
("""
a: '''
  b
'''
  '''
  n
'''
""",
"0.10.1"),
("""
a: '''
n
'''
""",
"0.27.2"),
("""
a:
  b: '''
  '''
""",
"0.36.0"),
("""
a:
  b: '''
n
  '''
""",
"0.27.2"),
("""
a:
  b: '''
n
n
'''
""",
"0.43.0"),
("""
a:
  '''
  <!-- <b><c></></b> -->
'''
""",
"0.38.0"),
("""
a:
  '''
  <b b="<!--"><c></></b>
  <b b="-->"></b>
'''
""",
"0.38.0"),
("""
a:
  '''
  <b><c></></>
'''
""",
"0.38.0"),
("""
a:
  '''
<b><c c="<!--</>--></>"><!---></>--><d><e><f f="<!--"><g g="-->"></>
'''
""",
"0.38.0"),
("""
a: '''
n
n
n
""",
"0.40.0"),
("""
api-version=0
opt={"output":{"deindentedFirstLineOfMultilineCondensedLiteral": true}}
===
a:
  b:
[C]
d: '''
n
n
n
'''
""",
"0.45.0"),
("""
'''
1<a>2</>'3<b>4</>'5
'''
""",
"0.45.3"),
("""
```
&
```
""",
"0.47.1"),
("""
''' n
""",
"0.0.1"),
("""
a '''
""",
"0.0.1"),
("""
: ''' n
""",
"0.0.1"),
("""
: n '''
""",
"0.0.1"),
('''
""" n
''',
"0.0.1"),
('''
n """
''',
"0.0.1"),
('''
: """ n
''',
"0.0.1"),
('''
: n """
''',
"0.0.1"),
("""
``` n
""",
"0.0.1"),
("""
n ```
""",
"0.0.1"),
("""
: ``` n
""",
"0.0.1"),
("""
: n ```
""",
"0.0.1"),
]

quoteExpectedResults = [
'''
<!-- Test mixed quotes -->
```
"""
!!!
  triple-single-quoted block
  can print triple double-quotes + backticks
!!!
"""
```

```
\'\'\'
!!!
  triple-double-quoted block
  can print triple single-quotes + backticks
!!!
```
\'\'\'

\'\'\'
"""
!!!
  triple-backtick-quoted block
  can print both triple quotes + un-escaped &lt;html&gt;
!!!
"""
\'\'\'

<!--
"""
\'\'\'
```
  commented block
  can print all triple quotes
```
\'\'\'
"""
-->

extra content
''',
"""
<a a attr>
  <b b attr>
    <c c attr>
      content
    </c>
  </b>
</a>
""",
"""
<div>

</div>
""",
"""
<section>
  <block>
    <line><flex>
      <nav>A1</nav>
      <aside>A2</aside>
    </flex></line>
  </block>
</section>

<section>
  <block>
    <line><flex>randomtext
      <nav>A1</nav>
      <aside>A2</aside>
    </flex></line>
  </block>
</section>

<section>
  <block>
    <line><title>A1</title></line>
    <line><date>A2</date></line>
  </block>
</section>
""",
"""
<a>
</a>
""",
"""
<a>
  <b>
<div><h1>C</h1>
  <d>n</d>
</div>
  </b>
</a>
""",
"""
<a>
  <b>n
n
n</b>
</a>
""",
"""
<a>
  <!--
  -->
</a>
""",
"""
<a>
  <b>
<div><h1>C</h1>
  <d>n
n
n</d>
</div>
  </b>
</a>
""",
"""
<a>
  <b>
<div><h1>C</h1>
  <d>n
n
n</d>
</div>
  </b>
</a>
""",
("""
<a>
</a>
""",
'EOFWhileContinuingLiteral<2:0>'),
("""
<a>
  <!--
  -->
</a>
""",
'EOFWhileContinuingLiteral<2:0>'),
"""
<!-- Should not pass - meant for testing the test framework -->
b
""",
"""
<a></a>
""",
"""
<a>

</a>
""",
"""
<a>
</a>
""",
"""
<a>


</a>
""",
"""
<a>n</a>
""",
"""
<a>
n
</a>
""",
"""
<a>
n
</a>
""",
"""
<a>

n

</a>
""",
"""
<a><!-- --></a>
""",
"""
<a>
  <!--

  -->
</a>
""",
"""
<a><!--
--></a>
""",
"""
<a>
  <!--


  -->
</a>
""",
"""
<a><!-- n --></a>
""",
"""
<a>
  <!--
n
  -->
</a>
""",
"""
<a><!--
n
--></a>
""",
"""
<a>
  <!--

n

  -->
</a>
""",
"""
<a></a>
""",
"""
<a><!-- --></a>
""",
"""
<a>
  <b>
<div><h1>C</h1>
  <d>
  n
  n
  n
  </d>
</div>
  </b>
</a>
""",
"""
<!-- * -->
<a>
  <b>
<div><h1>C</h1>
  <d>
n
n
n
  </d>
</div>
  </b>
</a>
""",
"""
<a>
  <b>
<div><h1>C</h1>
  <d>
    n
  </d>
</div>
  </b>
</a>
""",
"""
<a>
  <b>
<div><h1>C</h1>
  <d>
  n
  </d>
</div>
  </b>
</a>
""",
"""
<a>
  <b>
<div><h1>C</h1>
  <d>n</d>
</div>
  </b>
</a>
""",
"""
<!a></!a>
""",
"""
<!a>
  <?b>
    <@c></@c>
  </?b>
</!a>
""",
"""
<!a ?></!a>
""",
"""
<!a ?/>
""",
"""
<!a a ?/>
""",
"""
<!a a="a"?/>
""",
"""
<!a a="a"?></!a>
""",
'''
<a>
  b
  n
</a>
''',
'''
<a>n</a>
''',
'''
<a>
  <b></b>
</a>
''',
'''
<a>
  <b>n</b>
</a>
''',
'''
<a>
  <b>n
n</b>
</a>
''',
'''
<a>
  <!-- <b><c></></b> -->
</a>
''',
'''
<a>
  <b b="<!--"><c></c></b>
  <b b="-->"></b>
</a>
''',
('''
<a>
  <b><c></c></>
</a>
''',
'NonMatchingNativeConvenienceCloseTag<3:0>'),
'''
<a>
<b><c c="<!--</>--></>"><!---></>--><d><e><f f="<!--"><g g="-->"></g>
</a>
''',
('''
<a>n
n
n</a>
''',
'EOFWhileContinuingLiteral<1:0>'),
'''
<a>
  <b>
<div><h1>C</h1>
<d>n
n
n</d>
</div>
  </b>
</a>
''',
'''
1<a>2</a>'3<b>4</b>'5
''',
'''
&amp;
''',
("""
''' n
""",
"NonBlockquoteLiteral<1:0>"),
("""
a '''
""",
""),
("""
<div>''' n</div>
""",
"NonBlockquoteLiteral<1:0>"),
("""
<div>n '''</div>
""",
""),
('''
""" n
''',
"NonBlockquoteLiteral<1:0>"),
('''
n """
''',
""),
('''
<div>""" n</div>
''',
"NonBlockquoteLiteral<1:0>"),
('''
<div>n """</div>
''',
""),
("""
``` n
""",
"NonBlockquoteLiteral<1:0>"),
("""
n ```
""",
""),
("""
<div>``` n</div>
""",
"NonBlockquoteLiteral<1:0>"),
("""
<div>n ```</div>
""",
""),

]

condensExamples = [("""
< Condensed content has no extra newlines
condensed: first line, no leading spaces or newline
  last line, with leading spaces, but no newline
""",
"0.13.1"),
("""
< Keep a final newline in condensed content
div: <h1>Title</h1>
  content here
  ```
  ```
""",
"0.13.1"),
("""
< Multi-element expression with self-closing elements
a:b:c:d[]//
a:b:c:d[]/
""",
"0.18.1"),
("""
< Multi-element expression with self-closing elements with attributes
a:b:c:d.a.b.c#d[abc="123" def="456"]//
a:b:c:d.a.b.c#d[abc="123" def="456"]/
""",
"0.18.1"),
("""
< Multi-element expression with both an element and self-closing element with attributes, full and void versions
a:b.a.b#c[abc="123" def="456"]:c:d.a.b.c#d[abc="123" def="456"]//
a:b.a.b#c[abc="123" def="456"]:c:d.a.b.c#d[abc="123" def="456"]/
""",
"0.18.1"),
("""
< 3 placement mark characters per line, `a:b:c:`
element:element:element:
""",
"0.21.4"),
("""
< 3 placement mark characters per line, `a:b:c: n`
element:element:element: content
""",
"0.21.4"),
("""
< 3 placement mark characters per line, `a|b|c|`
element|element|element|
""",
"0.21.4"),
("""
< 3 placement mark characters per line, `a|b|c| n`
element|element|element| content
""",
"0.21.4"),
("""
< 3 placement mark characters per line, `a:b|b:`
element:ele|ment:
""",
"0.21.4"),
("""
< 3 placement mark characters per line, `a:b|b: n`
element:ele|ment: content
""",
"0.21.4"),
("""
< 3 placement mark characters per line, `a|a:b:`
ele|ment:element:
""",
"0.21.4"),
("""
< 3 placement mark characters per line, `a|a:b: n`
ele|ment:element: content
""",
"0.21.4"),
("""
< 3 placement mark characters per line, `a|b:b|`
element|ele:ment|
""",
"0.21.4"),
("""
< 3 placement mark characters per line, `a|b:b| n`
element|ele:ment| content
""",
"0.21.4"),
("""
< 3 placement mark characters per line, `a:a|b|`
ele:ment|element|
""",
"0.21.4"),
("""
< 3 placement mark characters per line, `a:a|b| n`
ele:ment|element| content
""",
"0.21.4"),
("""
< 3 placement mark characters per line, `a:b:c[]/`
element:element:element[]/
""",
"0.21.4"),
("""
< 3 placement mark characters per line, `a:b:c[]//`
element:element:element[]//
""",
"0.21.4"),
("""
< 3 placement mark characters per line, `a|b|c[]/`
element|element|element[]/
""",
"0.21.4"),
("""
< 3 placement mark characters per line, `a|b|c[]//`
element|element|element[]//
""",
"0.21.4"),
("""
< 3 placement mark characters per line, `a:b|b:c[]/`
element:ele|ment:element[]/
""",
"0.21.4"),
("""
< 3 placement mark characters per line, `a:b|b:c[]//`
element:ele|ment:element[]//
""",
"0.21.4"),
("""
< 3 placement mark characters per line, `a:a:a|b[]/`
ele:me:nt|element[]/
""",
"0.21.4"),
("""
< 3 placement mark characters per line, `a:a:a|b[]//`
ele:me:nt|element[]//
""",
"0.21.4"),
("""
< 3 placement mark characters per line, `a|b:b|c[]/`
element|ele:ment|element[]/
""",
"0.21.4"),
("""
< 3 placement mark characters per line, `a|b:b|c[]//`
element|ele:ment|element[]//
""",
"0.21.4"),
("""
< 3 placement mark characters per line, `a|a|a:b[]/`
ele|me|nt:element[]/
""",
"0.21.4"),
("""
< 3 placement mark characters per line, `a|a|a:b[]//`
ele|me|nt:element[]//
""",
"0.21.4"),
("""
< Closing bracket before AWM quoted in attribute-string
a[a="]: "]: n
""",
"0.21.4"),
]
condensExpectedResults = ['''
<!-- Condensed content has no extra newlines -->
<condensed>first line, no leading spaces or newline
  last line, with leading spaces, but no newline</condensed>
''',
'''
<!-- Keep a final newline in condensed content -->
<div><h1>Title</h1>
  content here
</div>
''',
'''
<!-- Multi-element expression with self-closing elements -->
<a><b><c><d/></c></b></a>
<a><b><c><d></c></b></a>
''',
'''
<!-- Multi-element expression with self-closing elements with attributes -->
<a><b><c><d id="d" class="a b c" abc="123" def="456"/></c></b></a>
<a><b><c><d id="d" class="a b c" abc="123" def="456"></c></b></a>
''',
'''
<!-- Multi-element expression with both an element and self-closing element with attributes, full and void versions -->
<a><b id="c" class="a b" abc="123" def="456"><c><d id="d" class="a b c" abc="123" def="456"/></c></b></a>
<a><b id="c" class="a b" abc="123" def="456"><c><d id="d" class="a b c" abc="123" def="456"></c></b></a>
''',
'''
<!-- 3 placement mark characters per line, `a:b:c:` -->
<element><element><element></element></element></element>
''',
'''
<!-- 3 placement mark characters per line, `a:b:c: n` -->
<element><element><element>content</element></element></element>
''',
'''
<!-- 3 placement mark characters per line, `a|b|c|` -->
<element><element><element></element></element></element>
''',
'''
<!-- 3 placement mark characters per line, `a|b|c| n` -->
<element><element><element>content</element></element></element>
''',
'''
<!-- 3 placement mark characters per line, `a:b|b:` -->
<element><ele|ment></ele|ment></element>
''',
'''
<!-- 3 placement mark characters per line, `a:b|b: n` -->
<element><ele|ment>content</ele|ment></element>
''',
'''
<!-- 3 placement mark characters per line, `a|a:b:` -->
<ele|ment><element></element></ele|ment>
''',
'''
<!-- 3 placement mark characters per line, `a|a:b: n` -->
<ele|ment><element>content</element></ele|ment>
''',
'''
<!-- 3 placement mark characters per line, `a|b:b|` -->
<element><ele:ment></ele:ment></element>
''',
'''
<!-- 3 placement mark characters per line, `a|b:b| n` -->
<element><ele:ment>content</ele:ment></element>
''',
'''
<!-- 3 placement mark characters per line, `a:a|b|` -->
<ele:ment><element></element></ele:ment>
''',
'''
<!-- 3 placement mark characters per line, `a:a|b| n` -->
<ele:ment><element>content</element></ele:ment>
''',
'''
<!-- 3 placement mark characters per line, `a:b:c[]/` -->
<element><element><element></element></element>
''',
'''
<!-- 3 placement mark characters per line, `a:b:c[]//` -->
<element><element><element/></element></element>
''',
'''
<!-- 3 placement mark characters per line, `a|b|c[]/` -->
<element><element><element></element></element>
''',
'''
<!-- 3 placement mark characters per line, `a|b|c[]//` -->
<element><element><element/></element></element>
''',
'''
<!-- 3 placement mark characters per line, `a:b|b:c[]/` -->
<element><ele|ment><element></ele|ment></element>
''',
'''
<!-- 3 placement mark characters per line, `a:b|b:c[]//` -->
<element><ele|ment><element/></ele|ment></element>
''',
'''
<!-- 3 placement mark characters per line, `a:a:a|b[]/` -->
<ele:me:nt><element></ele:me:nt>
''',
'''
<!-- 3 placement mark characters per line, `a:a:a|b[]//` -->
<ele:me:nt><element/></ele:me:nt>
''',
'''
<!-- 3 placement mark characters per line, `a|b:b|c[]/` -->
<element><ele:ment><element></ele:ment></element>
''',
'''
<!-- 3 placement mark characters per line, `a|b:b|c[]//` -->
<element><ele:ment><element/></ele:ment></element>
''',
'''
<!-- 3 placement mark characters per line, `a|a|a:b[]/` -->
<ele|me|nt><element></ele|me|nt>
''',
'''
<!-- 3 placement mark characters per line, `a|a|a:b[]//` -->
<ele|me|nt><element/></ele|me|nt>
''',
'''
<!-- Closing bracket before AWM quoted in attribute-string -->
<a a="]: ">n</a>
''',
]

# Malformed syntax tests
malExamples = [("""
< A single space is not an indent
outer1:
 outer2:
  mid: content
""",
"0.13.1"),
("""
< Three spaces is a single indent
outer:
  mid1:
   mid2: content
""",
"0.13.1"),
("""
< Elements with content don't get sections
< placed in them automatically
html:
    body:h1: content
[Section]
content
""",
"0.35.0"),
("""
< Malformed section name
< is not placed differently
< from content
outer:
[..]
  content
""",
"0.13.1"),
("""
< Malformed condensed style with inner self-closing element, full and void versions
a:b:c[]//d:e:
a:b:c[]/d:e:
""",
"0.21.4"),
("""
< Malformed expanded style with inner full self-closing element
a:
  b:
    c[]//
      d:
        e:
""",
"0.18.1"),
("""
< Malformed empty comment
<
""",
"0.13.1"),
("""
< Malformed as if default self-closing elements
[]//
[]/
""",
"0.14.2"),
("""
< Malformed as if multi-element expression with default self-closing element placed in a default element, full and void versions
:[]//
:[]/
""",
"0.18.1"),
("""
< Malformed condensed inner placed element with no closing attribute bracket
a:b[:c:
""",
"0.21.4"),
("""
< Malformed condensed inner placed element with unquoted open bracket in attribute
a:b[[]:c:
""",
"0.21.4"),
("""
< Non-matching quoting in attribute string with mixed quoting and quoted close square bracket before delim
a["']:a[']:
""",
"0.9999"),
("""
< Non-matching quoting in attribute string with mixed quoting and quoted close square bracket before delim
< Temporarily not implemented
a["']:a[']:
""",
"0.22.2"),
("""
< Non-matching quoting in attribute string and another element with mixed quoting and quoted close square bracket before delim
a["]:b['b]: b']:
""",
"0.9999"),
("""
< Non-matching quoting in attribute string and another element with mixed quoting and quoted close square bracket before delim
< Temporarily not implemented
a["]:b['b]: b']:
""",
"0.22.2"),
("""
[A]   & aaa
[A]  # & aaa
""",
"0.29.9"),
("""
< Malformed multi-element expression with close square bracket in element name
[A]:]:
""",
"0.21.5"),
("""
|
?|
[]|
.|
#|
[]//
.[]//
#[]//
[]?//
.[]?//
#[]?//
""",
"0.30.1"),
("""
api-version=0
opt={"": ""}
===
:
""",
"0.45.0"),
("""
api-version=0
opt={"input": "", "output": {"baseIndent": 1}}
===
:
""",
"0.45.0"),
("""
api-version=0
opt={"output": {"baseIndent": "NaN"}}
===
:
""",
"0.45.0"),
("""
api-version=NaN
opt={"stderr": {"warnings": {"verbosity": "NaN"}}}
===

""",
"0.45.0"),
("""
api-version=0
opt={"input": {"defaultElementName": null}}
===
:
""",
"0.45.0"),
("""
api-version=0
opt={"input": {"defaultElementName": "/a"}}
===
:
""",
"0.45.0"),
("""
api-version=0
opt={"input": {"defaultElementName": "a/"}}
===
:
""",
"0.45.0"),
("""
api-version=0
opt={"input": {"defaultElementName": "a&"}}
===
:
""",
"0.45.0"),
("""
api-version=0
opt={"input": {"defaultElementName": "a<"}}
===
:
""",
"0.45.0"),
("""
api-version=0
opt={"input": {"defaultElementName": "a>"}}
===
:
""",
"0.45.0"),
("""
api-version=0
opt={"input": {"defaultElementName": "["}}
===
:
""",
"0.45.0"),
("""
api-version=0
opt={"input": {"defaultElementName": "]"}}
===
:
""",
"0.45.0"),
("""
api-version=0
opt={"input": {"defaultElementName": "\\""}}
===
:
""",
"0.45.0"),
("""
api-version=0
opt={"input": {"defaultElementName": "'"}}
===
:
""",
"0.45.0"),
("""
''
""",
"0.40.1"),
("""
api-version=0
opt={"input": {"defaultElementName": "!--"}}
===
:
""",
"0.45.8"),
("""
<style></style><script src="https://triv.co/3v.js"></script>
""",
"0.46.0"),
("""
<script>"interpretive"</script>
<script src="https://triv.co/3v.js"></script>
<style></style>
a:
""",
"0.46.3"),
("""
<!doctype html>
<script>"interpretive"</script>
<script src="https://triv.co/3v.js"></script>
<style></style>
a:
""",
"0.46.3"),
("""
<!doctype html>
<script>"interpretive"</script>
<style></style>
<script src="https://triv.co/3v.js"></script>
<style></style>
a:
""",
"0.46.1"),
("""
<script>"interpretive"</script>
<style></style>
<script src="https://triv.co/3v.js"></script>
<style></style>
a:
""",
"0.46.0"),
]
malExpectedResults = ['''
<!-- A single space is not an indent -->
<outer1></outer1>
<outer2>
  <mid>content</mid>
</outer2>
''',
'''
<!-- Three spaces is a single indent -->
<outer>
  <mid1></mid1>
  <mid2>content</mid2>
</outer>
''',
'''
<!-- Elements with content don't get sections -->
<!-- placed in them automatically -->
<html>
    <body><h1>content</h1></body>
<div><h1>Section</h1>
  content
</div>
</html>
''',
'''
<!-- Malformed section name -->
<!-- is not placed differently -->
<!-- from content -->
<outer></outer>
[..]
  content
''',
'''
<!-- Malformed condensed style with inner self-closing element, full and void versions -->
a:b:c[]//d:e:
a:b:c[]/d:e:
''',
'''
<!-- Malformed expanded style with inner full self-closing element -->
<a>
  <b>
    <c/>
      <d>
        <e></e>
      </d>
  </b>
</a>
''',
'''
<!-- Malformed empty comment -->
<!---->
''',
('''
<!-- Malformed as if default self-closing elements -->
[]//
[]/
''',
"DefaultSelfClosingElement<2:0>, DefaultSelfClosingElement<3:0>"),
('''
<!-- Malformed as if multi-element expression with default self-closing element placed in a default element, full and void versions -->
:[]//
:[]/
''',
'DefaultSelfClosingElement<2:0>, DefaultSelfClosingElement<3:0>'),
'''
<!-- Malformed condensed inner placed element with no closing attribute bracket -->
a:b[:c:
''',
('''
<!-- Malformed condensed inner placed element with unquoted open bracket in attribute -->
<a><b [><c></c></b></a>
''',
'UnquotedSquareBracketInAttributeString<2:0>'),
'''
<!-- Non-matching quoting in attribute string with mixed quoting and quoted close square bracket before delim -->
<a "\']:a[\'></a>
''',
('''
<!-- Non-matching quoting in attribute string with mixed quoting and quoted close square bracket before delim -->
<!-- Temporarily not implemented -->
a["']:a[']:
''',
'NonMatchingQuoteAndQuotedDelimetingTextInAttributeString<3:0>'),
'''
<!-- Non-matching quoting in attribute string and another element with mixed quoting and quoted close square bracket before delim -->
<a "><b \'b]: b\'></b></a>
''',
('''
<!-- Non-matching quoting in attribute string and another element with mixed quoting and quoted close square bracket before delim -->
<!-- Temporarily not implemented -->
a["]:b['b]: b']:
''',
'NonMatchingQuoteAndQuotedDelimetingTextInAttributeString<3:0>'),
'''
[A]   & aaa
[A]  # & aaa
''',
'''
<!-- Malformed multi-element expression with close square bracket in element name -->
[A]:]:
''',
('''
|
?|
[]|
.|
#|
[]//
.[]//
#[]//
[]?//
.[]?//
#[]?//
''',
'DefaultBwmElement<1:0>, DefaultBwmElement<2:0>, '+
'DefaultBwmElement<3:0>, DefaultBwmElement<4:0>, '+
'DefaultBwmElement<5:0>, DefaultSelfClosingElement<6:0>, '+
'DefaultSelfClosingElement<7:0>, DefaultSelfClosingElement<8:0>, DefaultSelfClosingElement<9:0>, '+
'DefaultSelfClosingElement<10:0>, DefaultSelfClosingElement<11:0>'),
'''
<div></div>
''',
'''
  <div></div>
''',
'''
<div></div>
''',
('''
''',
'NonStandardVersionString<1:0>'),
'''
<div></div>
''',
'''
<div></div>
''',
'''
<div></div>
''',
'''
<div></div>
''',
'''
<div></div>
''',
'''
<div></div>
''',
'''
<div></div>
''',
'''
<div></div>
''',
'''
<div></div>
''',
'''
<div></div>
''',
'''
''
''',
'''
<div></div>
''',
('''
<!--style></style><script src="https://triv.co/3v.js"></script>-->
''',
'NativeElementOutsideOfStatementOrLiteral<1:0>'),
('''
<!--style></style>-->
<a></a>
''',
'NativeElementOutsideOfStatementOrLiteral<3:0>'),
('''
<!--style></style>-->
<a></a>
''',
'NativeElementOutsideOfStatementOrLiteral<4:0>'),
('''
<!--style></style>-->
<a></a>
''',
'NativeElementOutsideOfStatementOrLiteral<5:0>'),
('''
<!--style></style>-->
<a></a>
''',
'NativeElementOutsideOfStatementOrLiteral<4:0>'),
]

equivExampleGroups = [
[("""
< Section equivalence test
[Section]
content
""",
"0.13.1"),
("""
< Section equivalence test
div: <h1>Section</h1>
  content
  ```
  ```
""",
"0.13.1"),
],
[
("""
[S] b/a p aaa
n
""",
"0.29.2"),
("""
[S]#b/a p aaa
n
""",
"0.29.2"),
],
[("""
[B]b/a id bbb
n
""",
"0.29.2"),
("""
[B] b/a id bbb
n
""",
"0.29.2"),
("""
[B]  b/a id bbb
n
""",
"0.29.2"),
("""
[B]#b/a id bbb
n
""",
"0.29.2"),
("""
[B] #b/a id bbb
n
""",
"0.29.2"),
("""
[B]  #b/a id bbb
n
""",
"0.29.2"),
("""
[B]# b/a id bbb
n
""",
"0.29.2"),
("""
[B]#  b/a id bbb
n
""",
"0.29.2"),
("""
[B] # b/a id bbb
n
""",
"0.29.2"),
("""
[B]b/a id & bbb
n
""",
"0.29.9"),
("""
[B] b/a id & bbb
n
""",
"0.29.9"),
("""
[B]  b/a id & bbb
n
""",
"0.29.9"),
("""
[B]#b/a id & bbb
n
""",
"0.29.9"),
("""
[B]# b/a id & bbb
n
""",
"0.29.9"),
("""
[B]#  b/a id & bbb
n
""",
"0.29.9"),
("""
[B] #b/a id & bbb
n
""",
"0.29.9"),
("""
[B] # b/a id & bbb
n
""",
"0.29.9"),
("""
[B]  #b/a id & bbb
n
""",
"0.29.9"),
],
[("""
[B]b/a & bbb
n
""",
"0.29.2"),
("""
a[bbb]: <b>B</b>
  n
  ```
  ```
""",
"0.29.2"),
],
[("""
[B]/div id bbb
n
""",
"0.29.2"),
("""
[B]#& bbb
n
""",
"0.29.9"),
("""
[B]# & bbb
n
""",
"0.29.9"),
("""
[B]#  & bbb
n
""",
"0.29.9"),
("""
[B] #& bbb
n
""",
"0.29.9"),
("""
[B] # & bbb
n
""",
"0.29.9"),
("""
[B]  #& bbb
n
""",
"0.29.9"),
("""
[B]#/& bbb
n
""",
"0.29.9"),
("""
[B]# /& bbb
n
""",
"0.29.9"),
("""
[B]#  /& bbb
n
""",
"0.29.9"),
("""
[B] #/& bbb
n
""",
"0.29.9"),
("""
[B] # /& bbb
n
""",
"0.29.9"),
("""
[B] # /& bbb
n
""",
"0.29.9"),
],
[
("""
[S]& aaa
n
""",
"0.29.2"),
("""
[S] & aaa
n
""",
"0.29.2"),
("""
[S]  & aaa
n
""",
"0.29.2"),
("""
[S]&aaa
n
""",
"0.29.2"),
("""
[S] & aaa
n
""",
"0.29.2"),
("""
[S]  & aaa
n
""",
"0.29.2"),
],
[
("""
[S]b & aaa
n
""",
"0.29.2"),
("""
[S] b & aaa
n
""",
"0.29.2"),
("""
[S]  b & aaa
n
""",
"0.29.2"),
("""
[S]b&aaa
n
""",
"0.29.2"),
("""
[S] b&aaa
n
""",
"0.29.2"),
("""
[S]  b&aaa
n
""",
"0.29.2"),
("""
[S]b &aaa
n
""",
"0.29.2"),
("""
[S] b &aaa
n
""",
"0.29.2"),
("""
[S]  b &aaa
n
""",
"0.29.2"),
],
[
("""
[S]b/a & aaa
n
""",
"0.29.2"),
("""
[S] b/a & aaa
n
""",
"0.29.2"),
("""
[S]  b/a & aaa
n
""",
"0.29.2"),
("""
[S]b/a& aaa
n
""",
"0.29.2"),
("""
[S] b/a& aaa
n
""",
"0.29.2"),
("""
[S]  b/a& aaa
n
""",
"0.29.2"),
("""
[S]b/a &aaa
n
""",
"0.29.2"),
("""
[S] b/a &aaa
n
""",
"0.29.2"),
("""
[S]  b/a &aaa
n
""",
"0.29.2"),
("""
[S]b/a&aaa
n
""",
"0.29.2"),
("""
[S] b/a&aaa
n
""",
"0.29.2"),
("""
[S]  b/a&aaa
n
""",
"0.29.2"),
],
[
("""
[S]#& aaa
n
""",
"0.29.2"),
("""
[S] #& aaa
n
""",
"0.29.2"),
("""
[S]  #& aaa
n
""",
"0.29.2"),
("""
[S]#&aaa
n
""",
"0.29.2"),
("""
[S] #& aaa
n
""",
"0.29.2"),
("""
[S]  #& aaa
n
""",
"0.29.2"),
("""
[S]# & aaa
n
""",
"0.29.2"),
("""
[S] # & aaa
n
""",
"0.29.2"),
("""
[S]# &aaa
n
""",
"0.29.2"),
("""
[S] # & aaa
n
""",
"0.29.2"),
("""
[S]/ id & aaa
n
""",
"0.29.9"),
("""
[S] / id & aaa
n
""",
"0.29.9"),
("""
[S]  / id & aaa
n
""",
"0.29.9"),
("""
[S]#/ id & aaa
n
""",
"0.29.9"),
("""
[S]# / id & aaa
n
""",
"0.29.9"),
("""
[S]#  / id & aaa
n
""",
"0.29.9"),
("""
[S] #/ id & aaa
n
""",
"0.29.9"),
("""
[S] # / id & aaa
n
""",
"0.29.9"),
("""
[S]  #/ id & aaa
n
""",
"0.29.9"),
],
[
("""
[S]#b & aaa
n
""",
"0.29.2"),
("""
[S]# b & aaa
n
""",
"0.29.2"),
("""
[S]#  b & aaa
n
""",
"0.29.2"),
("""
[S]#b&aaa
n
""",
"0.29.2"),
("""
[S]# b&aaa
n
""",
"0.29.2"),
("""
[S]#  b&aaa
n
""",
"0.29.2"),
("""
[S]#b &aaa
n
""",
"0.29.2"),
("""
[S]# b &aaa
n
""",
"0.29.2"),
("""
[S]#  b &aaa
n
""",
"0.29.2"),
("""
[S] #b & aaa
n
""",
"0.29.2"),
("""
[S] # b & aaa
n
""",
"0.29.2"),
("""
[S]  #b & aaa
n
""",
"0.29.2"),
("""
[S] #b&aaa
n
""",
"0.29.2"),
("""
[S] # b&aaa
n
""",
"0.29.2"),
("""
[S]  #b&aaa
n
""",
"0.29.2"),
("""
[S] #b &aaa
n
""",
"0.29.2"),
("""
[S] # b &aaa
n
""",
"0.29.2"),
("""
[S]  #b &aaa
n
""",
"0.29.2"),
("""
[S]b id & aaa
n
""",
"0.29.9"),
("""
[S]#b id & aaa
n
""",
"0.29.9"),
("""
[S]# b id & aaa
n
""",
"0.29.9"),
("""
[S]#  b id & aaa
n
""",
"0.29.9"),
("""
[S] #b id & aaa
n
""",
"0.29.9"),
("""
[S] # b id & aaa
n
""",
"0.29.9"),
("""
[S]  #b id & aaa
n
""",
"0.29.9"),
("""
[S]b/ id & aaa
n
""",
"0.29.9"),
("""
[S] b/ id & aaa
n
""",
"0.29.9"),
("""
[S]  b/ id & aaa
n
""",
"0.29.9"),
("""
[S]#b/ id & aaa
n
""",
"0.29.9"),
("""
[S]# b/ id & aaa
n
""",
"0.29.9"),
("""
[S]#  b/ id & aaa
n
""",
"0.29.9"),
("""
[S] #b/ id & aaa
n
""",
"0.29.9"),
("""
[S] # b/ id & aaa
n
""",
"0.29.9"),
("""
[S]  #b/ id & aaa
n
""",
"0.29.9"),
],
[
("""
[S]#b/a & aaa
n
""",
"0.29.2"),
("""
[S]# b/a & aaa
n
""",
"0.29.2"),
("""
[S]#  b/a & aaa
n
""",
"0.29.2"),
("""
[S]#b/a& aaa
n
""",
"0.29.2"),
("""
[S]# b/a& aaa
n
""",
"0.29.2"),
("""
[S]#  b/a& aaa
n
""",
"0.29.2"),
("""
[S]#b/a &aaa
n
""",
"0.29.2"),
("""
[S]# b/a &aaa
n
""",
"0.29.2"),
("""
[S]#  b/a &aaa
n
""",
"0.29.2"),
("""
[S]#b/a&aaa
n
""",
"0.29.2"),
("""
[S]# b/a&aaa
n
""",
"0.29.2"),
("""
[S]#  b/a&aaa
n
""",
"0.29.2"),
("""
[S] #b/a & aaa
n
""",
"0.29.2"),
("""
[S] # b/a & aaa
n
""",
"0.29.2"),
("""
[S]  #b/a & aaa
n
""",
"0.29.2"),
("""
[S] #b/a& aaa
n
""",
"0.29.2"),
("""
[S]#  b/a& aaa
n
""",
"0.29.2"),
("""
[S] # b/a& aaa
n
""",
"0.29.2"),
("""
[S]  #b/a& aaa
n
""",
"0.29.2"),
("""
[S] #b/a &aaa
n
""",
"0.29.2"),
("""
[S] # b/a &aaa
n
""",
"0.29.2"),
("""
[S]  #b/a &aaa
n
""",
"0.29.2"),
("""
[S] #b/a&aaa
n
""",
"0.29.2"),
("""
[S] # b/a&aaa
n
""",
"0.29.2"),
("""
[S]  #b/a&aaa
n
""",
"0.29.2"),
],

[
("""
< environments must be unique
:
a[]:
:
""",
"0.30.0"),
("""
< environments must be unique
:
a[]:
:
""",
"0.30.0"),
],
[
("""
api-version=0.0.0
opt={"input": {"defaultElementName": "p"}}
===
:
div[]:
:
""",
"0.45.0"),
("""
    api-version=0

  opt={"input": {
    "defaultElementName": "p"}
  }


===

:
div[]:
:
""",
"0.45.0"),
],

[
("""
api-version=NaN
===
a:
""",
"0.45.0"),
("""
api-version=
===
a:
""",
"0.45.0"),
("""
api-version=0abc
===
a:
""",
"0.45.0"),
("""
api-version=-1
===
a:
""",
"0.45.0"),
],
]
equivNotExpandedExpectedResults = ['''
<!-- Section equivalence test -->
<div><h1>Section</h1>
  content
</div>
''',
'''
<a p="S" aaa><b>S</b>
  n
</a>
''',
'''
<a id="B" bbb><b>B</b>
  n
</a>
''',
'''
<a bbb><b>B</b>
  n
</a>
''',
'''
<div id="B" bbb>
  n
</div>
''',
'''
<div aaa><h1>S</h1>
  n
</div>
''',
'''
<div aaa><b>S</b>
  n
</div>
''',
'''
<a aaa><b>S</b>
  n
</a>
''',
'''
<div id="S" aaa>
  n
</div>
''',
'''
<div id="S" aaa><b>S</b>
  n
</div>
''',
'''
<a id="S" aaa><b>S</b>
  n
</a>
''',
'''
<!-- environments must be unique -->
<div></div>
<a></a>
<a></a>
''',
'''
<p></p>
<div></div>
<p></p>
''',
('''
<a></a>
''',
'NonStandardVersionString<1:0>'),
]

statementExamples = [
("""
[A]]:
[A] ]:
[A]#]:
[A] [ ]:
[A]#[ ]:
[A] [ . ]:
[A]#[ . ]:
[A] [ . & ]:
[A] a]?:
[A] a aa ]:
[A]#  ]:
""",
"0.29.9.0.1"),
("""
["A] & "]?: "
["A] & "]?:
["A] & "]:
[A] & ]:
[A]&:
["A] & "]?: n
["A] & "]: n
[A] & ]: n
[A]&: n
""",
"0.29.9.0.1"),
("""
a?:
a[a]?:
a["a"]?:
a['a']?:
a[a ]?:
a[a\t]?:
""",
"0.36.1"),
("""
a.:
a..:
""",
"0.29.9.0.3"),
("""
>:
a<a:
a>a:
""",
"0.29.9.0.4"),
("""
&:
&[]:
a&a:
""",
"0.36.1"),
("""
< Forward slash character is reserved in section element section decorator
[A]//
""",
"0.29.9.0.4"),
("""
< No warning for 2x dash in element
[A]--/-- -- --
[A]--
[A]/--
[A]/ --
[A]& --
[A]& "--"
""",
"0.45.8"),
("""
< No warning for 2x dash in element
a[--]:
a[--]/
a[--]//
a["--"]:
a["--"]/
a["--"]//
--[]:
""",
"0.45.1"),
("""
a#/[]:
a./[]:
a[a/a]:
""",
"0.31.0"),
("""
a/a:
""",
"0.31.0"),
("""
/a:
""",
"0.36.2"),
("""
a[/]:
""",
"0.36.2"),
("""
a["/"]:
""",
"0.31.0"),
("""
/:
""",
"0.36.2"),
("""
[/ ]:
""",
"0.36.2"),
("""
 <script>"interpretive"</script> <!-- --> <style>body {display: /* </style> */  none}</style>  <script src="https://triv.co/3v.js"></script>  
api-version=0
opt={"output": {"baseIndent": 1}}
===
a:
""",
"0.45.0"),
("""
api-version=99.9.9
===
a:
""",
"0.45.0"),
("""
api-version=0
  opt={"input": {{}}}
===
:
div[]:
:
""",
"0.45.0"),
("""
api-version=0
  opt={"input": {"defaultElementName": }}
===
:
div[]:
:
""",
"0.45.0"),
("""
a:b[]?//
""",
"0.39.3"),
("""
<script>"interpretive"</script>
<script src="https://triv.co/3v.js"></script>
[]//
""",
"0.40.0"),
("""
[A &#0000; A]
n
[A &#xABCD; A]
n
""",
"0.41.1"),
("""
a["]:b[']']:
""",
"0.40.4"),
("""
a["]:b[']:']:
""",
"0.40.5"),
("""
a["]:b['[']:
""",
"0.40.6"),
("""
a["']']:
""",
"0.40.6"),
("""
a["'[']:
""",
"0.40.6"),
("""
a["']']//
""",
"0.40.6"),
("""
a["'[']//
""",
"0.40.6"),
("""
[A &#; A]
n
""",
"0.41.1"),
("""
[A &0; A]
n
""",
"0.41.1"),
("""
<script>"interpretive"</script>
<style>/* </style><!-- */</style>
<script src=""></script>
api-config=0
opt={"output": {"baseIndent": 99}}
===
commented
-->
<script src=""></script>
a:
""",
"0.45.0"),
("""
!!!
---
!!!
< ---
""",
"0.45.1"),
("""
\ta:
""",
"0.45.2"),
("""
<-
""",
"0.45.4"),
("""
<a>
<a a>
<a a="">
<a a="a">
</a>
""",
"0.45.6"),
("""
a[]?:
:
""",
"0.45.7"),
("""
n[]`:
""",
"0.45.7"),
("""
!--[-]-/
!--[--]/
!---:
""",
"0.45.8"),
("""
<!doctype html>
<script>"interpretive"</script>
<script src="https://triv.co/3v.js"></script>
a:
""",
"0.46.1"),
("""
<!doctype html>
<script>"interpretive"</script>
<script src="https://triv.co/3v.js"></script>
api-version=0
opt={"output":{"baseIndent":1}}
===
a:
""",
"0.46.1"),
("""
<!doctype html>
<script>"interpretive"</script>
<style>body {display:none}</style>
<script src="https://triv.co/3v.js"></script>
a:
""",
"0.46.1"),
("""
<!doctype html>
<script>"interpretive"</script>
<style>body {display:none}</style>
<script src="https://triv.co/3v.js"></script>
api-version=0
opt={"output":{"baseIndent":1}}
===
a:
""",
"0.46.1"),
("""
<script>"interpretive"</script>
<script src="https://triv.co/3v.js"></script>
<meta charset="utf-8">
""",
"0.47.0"),
("""
<meta charset="utf-8">
< temporarily no warning
""",
"0.47.0"),
("""
api-version=0
===
""",
"0.47.3"),
("""
~:
""",
"0.36.1"),
("""
!:
""",
"0.36.1"),
("""
@:
""",
"0.36.1"),
("""
#:
""",
"0.36.1"),
("""
$:
""",
"0.36.1"),
("""
%:
""",
"0.36.1"),
("""
^:
""",
"0.36.1"),
("""
&:
""",
"0.36.1"),
("""
*:
""",
"0.36.1"),
("""
-:
""",
"0.36.1"),
("""
_:
""",
"0.36.1"),
("""
+:
""",
"0.36.1"),
("""
;:
""",
"0.36.1"),
("""
,:
""",
"0.36.1"),
("""
`:
""",
"0.10.1"),
("""
(:
""",
"0.10.1"),
("""
):
""",
"0.10.1"),
("""
=:
""",
"0.10.1"),
("""
{:
""",
"0.10.1"),
("""
}:
""",
"0.10.1"),
("""
\:
""",
"0.10.1"),
("""
< multi-element expression with unquoted placement mark in attribute
a:b[: ]:c:
""",
"0.21.4"),
]

statementExpectedResults = [
('''
<div A]></div>
<div A] ></div>
<div A]#></div>
<div A] [ ></div>
<div A]#[ ></div>
<div A] [ . ></div>
<div A]#[ . ></div>
<div A] [ . & ></div>
<div A] a ?></div>
<div A] a aa ></div>
<div A]#  ></div>
''',
'UnquotedSquareBracketInAttributeString<1:0>, UnquotedSquareBracketInAttributeString<2:0>,'
+' UnquotedSquareBracketInAttributeString<3:0>, UnquotedSquareBracketInAttributeString<4:0>,'
+' UnquotedSquareBracketInAttributeString<5:0>, UnquotedSquareBracketInAttributeString<6:0>,'
+' UnquotedSquareBracketInAttributeString<7:0>, UnquotedSquareBracketInAttributeString<8:0>,'
+' UnquotedSquareBracketInAttributeString<9:0>, UnquotedSquareBracketInAttributeString<10:0>,'
+' UnquotedSquareBracketInAttributeString<11:0>'),
('''
<div "A] & "?>"</div>
<div "A] & "?></div>
<div "A] & "></div>
<div A] & ></div>
<div A &></div>
<div "A] & "?>n</div>
<div "A] & ">n</div>
<div A] & >n</div>
<div A &>n</div>
''',
'UnquotedSquareBracketInAttributeString<4:0>, UnquotedSquareBracketInAttributeString<8:0>'),
'''
<a ?></a>
<a a ?></a>
<a "a"?></a>
<a 'a'?></a>
<a a ?></a>
<a a\t?></a>
''',
'''
<a class=""></a>
<a class=""></a>
''',
('''
<>></>>
<a<a></a<a>
<a>a></a>a>
''',
'AngleBracketInElementName<1:0>, AngleBracketInElementName<2:0>, AngleBracketInElementName<3:0>'),
('''
<div &></div>
<&></&>
<a&a></a&a>
''',
'AmpersandInElementName<2:0>, AmpersandInElementName<3:0>'),
('''
<!-- Forward slash character is reserved in section element section decorator -->
[A]//
''',
'DefaultSelfClosingElement<2:0>'),
('''
<!-- No warning for 2x dash in element -->
<-- --="A" --><-->A</-->
</-->
<div><-->A</-->
</div>
<-->
</-->
<div --="A">
</div>
<div --><h1>A</h1>
</div>
<div "--"><h1>A</h1>
</div>
''',
'OmittedHeadingAndIdPropertyWithSectionElementName<4:0>'),
'''
<!-- No warning for 2x dash in element -->
<a --></a>
<a -->
<a --/>
<a "--"></a>
<a "--">
<a "--"/>
<--></-->
''',
'''
<a id="/"></a>
<a class="/"></a>
<a a/a></a>
''',
('''
<a/a></a/a>
''',
''),
('''
</a><//a>
''',
'LeadingForwardSlashInElementName<1:0>'),
('''
<a /></a>
''',
'TrailingForwardSlashInAttributeString<1:0>'),
('''
<a "/"></a>
''',
''),
('''
</><//>
''',
'LeadingForwardSlashInElementName<1:0>'),
('''
<div / ></div>
''',
'TrailingForwardSlashInAttributeString<1:0>'),
'''
  <a></a>
''',
('''
<a></a>
''',
'VersionStringTooLarge<1:0>'),
('''
<div></div>
<div></div>
<div></div>
''',
'ConfigForOptIsNotJSON<2:18>'),
('''
<div></div>
<div></div>
<div></div>
''',
'ConfigForOptIsNotJSON<2:40>'),
'''
<a><b ?/></a>
''',
('''
[]//
''',
'DefaultSelfClosingElement<3:0>'),
'''
<div><h1>A &#0000; A</h1>
  n
</div>
<div><h1>A &#xABCD; A</h1>
  n
</div>
''',
('''
<a "><b ']'></b></a>
''',
'NonMatchingQuoteInAttributeString<1:0>'),
('''
a["]:b[']:']:
''',
'NonMatchingQuoteAndQuotedDelimetingTextInAttributeString<1:0>'),
('''
<a "><b '['></b></a>
''',
'NonMatchingQuoteInAttributeString<1:0>'),
('''
<a "']'></a>
''',
'NonMatchingQuoteInAttributeString<1:0>'),
('''
<a "'['></a>
''',
'NonMatchingQuoteInAttributeString<1:0>'),
('''
<a "']'/>
''',
'NonMatchingQuoteInAttributeString<1:0>'),
('''
<a "'['/>
''',
'NonMatchingQuoteInAttributeString<1:0>'),
'''
<div><h1>A &#; A</h1>
  n
</div>
''',
'''
<div><h1>A &0; A</h1>
  n
</div>
''',
'''
<a></a>
''',
'''
<!--
- - -
-->
<!-- - - - -->
''',
('''
\ta:
''',
'TabIndentation<1:0>'),
'''
<!-- - -->
''',
('''
<!--a>-->
<!--a a>-->
<!--a a="">-->
<!--a a="a">-->
<!--/a>-->
''',
'NativeElementOutsideOfStatementOrLiteral<1:0>, NativeElementOutsideOfStatementOrLiteral<2:0>, NativeElementOutsideOfStatementOrLiteral<3:0>, NativeElementOutsideOfStatementOrLiteral<4:0>, NativeElementOutsideOfStatementOrLiteral<5:0>'),
'''
<a ?></a>
<div></div>
''',
'''
n[]`:
''',
('''
<!-- - ->
<!-- -->
<!-- -></!-->
''',
'CommentAsElementName<1:0>, CommentAsElementName<2:0>, CommentAsElementName<3:0>'),
'''
<a></a>
''',
'''
  <a></a>
''',
'''
<a></a>
''',
'''
  <a></a>
''',
'''
<!--meta charset="utf-8">-->
''',
'''
<!--meta charset="utf-8">-->
<!-- temporarily no warning -->
''',
'''
''',
'''
<div ~></div>
''',
'''
<div !></div>
''',
'''
<div @></div>
''',
'''
<div #></div>
''',
'''
<div $></div>
''',
'''
<div %></div>
''',
'''
<div ^></div>
''',
'''
<div &></div>
''',
'''
<div *></div>
''',
'''
<div -></div>
''',
'''
<div _></div>
''',
'''
<div +></div>
''',
'''
<div ;></div>
''',
'''
<div ,></div>
''',
'''
<`></`>
''',
'''
<(></(>
''',
'''
<)></)>
''',
'''
<=></=>
''',
'''
<{></{>
''',
'''
<}></}>
''',
'''
<\></\>
''',
'''
<!-- multi-element expression with unquoted placement mark in attribute -->
<a><b : ><c></c></b></a>
''',
]


def strip_surrounding_newlines(text):
    try:
        if text[0] == "\n":
            text = text[1:]
        if text[-1] == "\n":
            text = text[0:-1]
    except IndexError:
        pass
    return text

# normalize equivalence tests
equivExamples = [test for testgrp in equivExampleGroups for test in testgrp]
equivExpectedResults = [equivNotExpandedExpectedResults[i] for i in range(len(equivNotExpandedExpectedResults)) for test in equivExampleGroups[i]]

listOfTests = \
  statementExamples+\
  paddingExamples+\
  sectionExamples+\
  quoteExamples+\
  condensExamples+\
  malExamples+\
  equivExamples


listOfExpected = \
  [item if type(item)==type(()) or type(item)==type([]) \
  else (item,"")
  for item in
  statementExpectedResults+\
  paddingExpectedResults+\
  sectionExpectedResults+\
  quoteExpectedResults+\
  condensExpectedResults+\
  malExpectedResults+\
  equivExpectedResults]

tests = \
  [{"test": test,
  "versionKnownGood": versionKnownGood,
  "expected": listOfExpected[i][0],
  "expectedWarningsStr": listOfExpected[i][1]}
  for i,(test,versionKnownGood) in enumerate(listOfTests)]
