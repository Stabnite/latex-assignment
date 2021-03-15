import re
from packages.commands import commands
from packages.book import raw_book


def latex_question(raw_question):
    numbers = re.findall('\n[∗]?\d+\. |^\d+. ',raw_question) # find question number
    if not numbers:
        return 1, 'Number Error: Question must begin with number followed by point.'
    
    
    raw_question = raw_question.split(numbers[0],1)[1]
    if len(numbers) > 1: # stop at one question only
        raw_question = raw_question.split(numbers[1],1)[0]

    
    parts_delimiter = re.sub('\([^\(\)]*\)', '',raw_question) # find non balanced  brackets
    number = numbers[0][:-2].replace('\n','')
    heading = re.split('\s+a\)', raw_question)[0].replace('\r\n',' ') 
    print('\n\n\n ' + '-'*40)
    print('number: ', number)
    print('\nheading: ', heading)

    raw_question = re.split('\n\d+\. ',raw_question)[0] # ignore incomplete or extra questions
    

    parts = re.split('a\)', raw_question, maxsplit=1)[1:]
    parts_delimiter = re.sub('([a-z])\s*\)', r'\1)', parts_delimiter) # [a-z] ) -> [a-z])
    parts_delimiter = re.findall('\r?\n?\s*?[a-z]\)', parts_delimiter) # find [a-z])
    
    print('\nparts_delimiters: ',parts_delimiter)
    
    latex_question = f'\\begin{{question}}{{{number}}}'
    latex_question += '\n    ' + latex_symbols(heading)[1]

    if parts:
        parts = parts[0]
        print('parts: ', parts)
        parts = re.sub('([a-z])\s*\)', r'\1)', parts)
        
        # parts = re.sub('(\r\n)|\n', ' ', parts)
        for delimiter in parts_delimiter:
            parts = parts.replace(delimiter,'_delimiter')
        parts = parts.split('_delimiter')

        print('\nsplit parts: ', parts)
        latex_question += '\n\n    \\begin{parts}'

        for part in parts:
            # part = parts[i][1:].replace('\r\n',' ')
            latex_question += f'\n        \\part {latex_symbols(part)[1]}'
            latex_question += '\n        \\sol{}\n'
        latex_question = latex_question[:-1]
        latex_question += '\n    \\end{parts}'
    else:
        latex_question += '\n    \\sol{}'
    
    latex_question += '\n\end{question}'

    return 0, latex_question


def latex_symbols(raw):
    simple_symbols = '([\[\]\(\)]=+-)'

    raw = re.sub('(\d)', r'$\1$', raw) # 4 -> $4$
    raw = re.sub('([^A-Za-z\d.,!;\s\$“”?’\'])', r'$\1$', raw) # simple math symbol -> $symbol$
    raw = re.sub('([^\w’\'])(\d*[b-zB-Z]\d*)([^\w’\'])', r'\1$\2$\3', raw) # 2n -> $2n$

    raw = re.sub(simple_symbols, r'$\1$', raw) # simple_symbols -> $simple_symbols$
    raw = re.sub('\$\s*\$', '', raw) # $ $ -> 
    raw = re.sub('\$\s*(,)\s\$', r'\1', raw) 

    for (command,symbol) in commands: ## symbol -> command
        raw = raw.replace(symbol,f' {command} ')

    raw = re.sub('√(\$)?\s*([A-Za-z\d]*)', r'\\sqrt{\2}\1', raw) # √ 3n -> \sqrt{3n}
    raw = re.sub('([^\w\s]\s*)([aA])(\s*[^\w\s])', r'\1$\2$\3', raw) # = A. -> =$A$.
    raw = re.sub('([a-z][A-Z])', r'$\1$', raw) # xP -> $xP$
    raw = re.sub('\$(\s*[.]\s*)\$', r'\1', raw) # $4$ . $3$ -> $4 . 3$
    raw = re.sub('(\w\s+)(A)', r'\1$\2$', raw) # let A -> let $A$
    raw = re.sub('\$\s*\$', '', raw) # $ $ -> 
    raw = re.sub('(\$\(\$)\s*|\s*(\$\)\$)', r'\1\2', raw) # ( hi ) -> (hi)
    raw = re.sub('[\r?\n?]+', ' ', raw) # \n ->
    raw = raw.replace(' \\ ', '  ') # remove lone backslashes

    return 0, raw

def parse_assignment(raw):
    raw = re.sub('\([^\(\)]*\)', ' ', raw) # remove `(18 marks)'
    assignment_number = re.findall('Assignment\s*#(\d+)', raw)
    if assignment_number:
        assignment_number = assignment_number[0]
    numbers = re.findall('Section\s*(\d+.\d)|\s*Exercise\s*(\d+)', raw)
    
    if not numbers:
        return 1, 'Section Error: No sections found.'
    
    numbers = [number for section in numbers for number in list(filter(None, section))]

    res = []
    section = []
    for number in numbers:
        if '.' in number:
            res.append(section)
            section = [number]
        else:
            section.append(number)
    res.append(section)
    res = res[1:] # remove first empty list
    res = [assignment_number] + res
    return 0, res


def latexify(parsed_sections):
    assignment_number = parsed_sections[0]

    if type(assignment_number) != str:
        assignment_number = ''
    else:
        parsed_sections.pop(0)

    latex = f'''\\documentclass[10pt]{{exam}}

\\usepackage{{amsmath,amsthm,amssymb}}
\\usepackage[margin=1in]{{geometry}}
\\usepackage{{ulem}}

\\newcommand{{\\sol}}[1]{{\\begin{{solution}}#1\\end{{solution}}}}
\\renewcommand{{\\questionlabel}}{{\\textbf{{\\thequestion.}}}}

\\newenvironment{{question}}[1]{{
\\begin{{questions}}
\\setcounter{{question}}{{#1}}
\\addtocounter{{question}}{{-1}}
\\question \\hspace{{-0.304cm}}
}}{{%
\\end{{questions}}
}}

\\printanswers %comment this to hide answers

\\title{{1DM3 Assignment \\#{assignment_number}}}
\\author{{First Last \\#400000000}}

\\begin{{document}} 

\\maketitle

\\part*{{Exercises}}'''

    for section in parsed_sections:
        if section:
            section_number = section[0]
        else:
            return 0, "Error. No sections found."
        latex += f'\n\n\\section*{{Section {section_number}}}\n'
        questions = section[1:]

        for question in questions:
            latex += '\n'
            print(book_exercises[section_number])
            res = latex_question(book_exercises[section_number][question])
            exit_code = res[0]
            latexed_question = res[1]
            
            if exit_code:
                return exit_code, latexed_question
            else:
                latex += latexed_question
            
            latex += '\n'
    
    latex += '\n\n\\end{document}'

    return 0, latex


def find_exercises(raw_exercises):
    raw_exercises = raw_exercises.replace('∗','\n')
    raw_exercises = [question.replace('∗', '') for question in re.split('(\n\d+\. )', raw_exercises)[1:]]
    raw_exercises = {raw_exercises[i]: raw_exercises[i+1] for i in range(0, len(raw_exercises), 2)}
    return raw_exercises

# sections in book
sections = [ 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 2.1
           , 2.2, 2.3, 2.4, 2.5, 2.6
           , 3.1, 3.2, 3.3
           , 4.1, 4.2, 4.3, 4.4, 4.5, 4.6
           , 5.1, 5.2, 5.3, 5.4, 5.5
           , 6.1, 6.2, 6.3, 6.4, 6.5, 6.6
           , 7.1, 7.2, 7.3, 7.4
           , 8.1, 8.2, 8.3, 8.4, 8.5, 8.6
           , 9.1, 9.2, 9.3, 9.4, 9.5, 9.6
           , 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8
           , 11.1, 11.2, 11.3, 11.4, 11.5
           , 12.1, 12.2, 12.3, 12.4, 13.1, 13.2, 13.3, 13.4, 13.5]

book_exercises = {}

# find all exercises in book
raw_exercises = re.findall('(\nExercises\n)(.*?)(\n\d+\.\d+\s+[A-Zn][a-z’–-]+(\s*[A-Za-z’–-])*|\nKey Terms and Results)\n', raw_book, re.DOTALL)


# loop through all exercises in book
for i, section in enumerate(raw_exercises):
    
    # find and parse exercises for each section
    section_exercises = find_exercises(section[1])
    
    # add exercises to dictionary
    # {'exercise number': 'excercise stuff'}
    d = {}
    for number in section_exercises:
        d[number[1:-2]] =  number[1:] + section_exercises[number]
    
    # add section exercises to the rest
    # {'section number': {'excercise number': 'excercise stuff'}}}
    book_exercises[str(sections[i])] = d

for key in book_exercises:
    print(key)
