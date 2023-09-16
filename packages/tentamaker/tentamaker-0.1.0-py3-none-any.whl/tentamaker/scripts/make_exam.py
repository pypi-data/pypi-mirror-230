# Copyright (C) 2023 Anders Logg
# Licensed under the MIT License

import sys, os, re, random, toml, subprocess, shutil

from tentamaker import _version, _config_path_local
from tentamaker import _dir_config, _dir_tex, _dir_pdf, _dir_png, _dir_tmp
from tentamaker import _config, _pool, _header, _footer, _config, _snapshot


def uniq(seqeuence):
    "Return unique elements in sequence"
    return sorted(list(set(seqeuence)))


def exam_prefix(exam_date, code, _exam, include_solutions=True):
    "Return prefix for exam file"
    tes = "-tes" if not include_solutions else ""
    return f"{_exam.lower()}-{code.lower()}-{exam_date}{tes}"


def load_questions():
    "Load questions from pool"

    # Read pool as lines
    with open(_config_path_local / _pool) as f:
        lines = f.read().split("\n")

    # Create empty dictionary of questions
    questions = {}

    # Regular expression for matching start of question
    question_pattern = r"^%\s+[A-Za-z]\.\d+\.\d+$"

    # Parse questions
    num_lines = len(lines)
    i = 0
    while i < num_lines:
        line = lines[i]
        if bool(re.match(question_pattern, line)):
            # Parse key
            label = line.split("%")[1].strip().split(".")
            part = label[0]
            number = int(label[1])
            index = int(label[2])
            key = (part, number, index)

            # State machine for parsing each question
            Q, A, S = 0, 1, 2
            state = Q

            # Parse question, answer and solution
            question = ""
            answer = ""
            solution = ""
            for j in range(i + 1, num_lines):
                line = lines[j]

                # Change state
                if line.startswith("%"):
                    if state is Q:
                        state = A
                    elif state is A:
                        state = S
                    else:
                        break

                # Store line
                if state is Q:
                    question += "\n" + line
                elif state is A:
                    answer = line[1:]
                    state = S
                elif state is S:
                    solution += "\n" + line

            # Move to last line
            i = j

            # Store question
            questions[key] = (question.strip(), answer.strip(), solution.strip())

        # Move to next line
        i += 1

    print(f"Loaded {len(questions)} questions from pool")

    return questions


def create_selection(questions, randomize):
    "Create selection of questions"

    # Load config
    config = toml.load(_config_path_local / _config)

    # Seed random number generator
    if randomize:
        if "seed" in config:
            seed = config["seed"]
        else:
            seed = os.urandom(4)
        print(f"Randomizing questions using seed {seed}")
        random.seed(os.urandom(4))

    # Get keys and parts
    keys = sorted(questions.keys())
    parts = uniq(key[0] for key in keys)

    # Iterate over parts
    selection = []
    for part in parts:
        # Iterate over numbers
        _keys = [k for k in keys if k[0] == part]
        numbers = uniq(k[1] for k in _keys)
        for number in numbers:
            # Get indices
            __keys = [k for k in _keys if k[1] == number]
            indices = [k[2] for k in __keys]

            # Randomize or pick last question
            if randomize:
                index = indices[random.randrange(len(indices))]
            else:
                index = indices[-1]

            # Append to selection
            key = (part, number, index)
            selection.append(key)

    print(f"Created selection of {len(questions)} questions")
    print()
    for part, number, index in selection:
        print(f"  {part}.{number}.{index}")
    print()

    return selection


def build_pdf(questions, selection, exam_date, include_solutions=True, verbose=False):
    "Build PDF file from selection of questions"

    tex = ""

    # Load config
    config = toml.load(_config_path_local / _config)

    # Add header
    with open(_dir_config / _header) as f:
        examiner_first = config["examiner"].split(" ")[0].title()
        header = f.read()
        header = header.replace("_CODE", config["_code"])
        header = header.replace("CODE", config["code"].upper())
        header = header.replace("TITLE", config["title"])
        header = header.replace("EXAMINER_FIRST", examiner_first)
        header = header.replace("_EXAMINER", config["_examiner"].title())
        header = header.replace("EXAMINER", config["examiner"])
        header = header.replace("_EXAM", config["_exam"].title())
        header = header.replace("EXAM_DATE", exam_date)
        header = header.replace("_PHONE", config["_phone"].title())
        header = header.replace("PHONE", config["phone"])
        header = header.replace("DEPARTMENT", config["department"].upper())
        header = header.replace("SCHOOL", config["school"])
        header = header.replace("GOOD_LUCK", config["_good_luck"].capitalize())
        header = header.replace("_TOOLS", config["_tools"].title())
        header = header.replace("TOOLS", config["tools"].title())
        tex += header

    # Add questions
    parts = uniq(key[0] for key in selection)
    for part in parts:
        # Begin part
        tex += "\\newpage\n"
        tex += f"\\large \\textbf{{{config['_exam'].title()} {config['code'].upper()} {exam_date}}} \\hfill \\textbf{{{config['_part'].title()} {part}}}\n"
        tex += "\\\\[-1em]\n"
        tex += "\\hrule\n"
        tex += "\\begin{itemize}\n"
        tex += "\\setlength\itemsep{1em}\n"

        # Iterate over questions
        _selection = [k for k in selection if k[0] == part]
        for key in _selection:
            # Add question
            part, number, index = key
            question, answer, solution = questions[key]
            tex += "\\item[\\textbf{%s.%d}]\n" % (part, number)
            tex += question + "\n"

        # End part
        tex += "\\end{itemize}\n\n"

    # Add solutions
    if include_solutions:
        tex += "\\newpage\n"
        tex += f"\\large \\textbf{{{config['_exam'].title()} {config['code'].upper()} {exam_date}}} \\hfill \\textbf{{{config['_solutions'].title()}}}\n"
        tex += "\\\\[-1em]\n"
        tex += "\\hrule\n"
        tex += "\\begin{itemize}\n"
        tex += "\\setlength\itemsep{1em}\n"
        for key in selection:
            part, number, index = key
            question, answer, solution = questions[key]
            _bp = "\\begin{python}"
            _ep = "\\end{python}"
            if _bp in question:  # Remove Python code in solution
                question = question.split(_bp)[0] + question.split(_ep)[1]
            tex += f"\\item[\\textbf{{{part}.{number}}}]\n"
            tex += "\\it\n"
            tex += question
            tex += "\n\n"
            tex += "\\vspace{-0.35cm}\n"
            tex += "\\hdashrule{14.6cm}{1pt}{1pt}\n\n"
            tex += "\\rm\n"
            tex += solution
            tex += "\n\n"
            tex += f"\\textbf{{{config['_answer'].title()}:}} {answer}\n\n"
            tex += "\n\n"
            tex += "\\vspace{0.5cm}\n"
            tex += "\\hrule\n"
        tex += "\\end{itemize}\n\n"

    # Add footer
    with open(_config_path_local / _footer) as f:
        footer = f.read()
        tex += footer

    # Set file names
    prefix = exam_prefix(exam_date, config["code"], config["_exam"], include_solutions)
    tex_file = prefix + ".tex"
    pdf_file = prefix + ".pdf"

    # Write TeX to file(s)
    with open(_dir_tex / tex_file, "w") as f:
        f.write(tex)
    with open(_dir_tmp / tex_file, "w") as f:
        f.write(tex)
    print(f"Exam written to {_dir_tex / tex_file}")

    # Build PDF
    os.chdir(_dir_tmp)
    subprocess.run(["pdflatex", tex_file], capture_output=(not verbose))
    os.chdir("..")
    shutil.copy(_dir_tmp / pdf_file, _dir_pdf)
    print(f"Exam written to {_dir_pdf / pdf_file}")


def build_png(questions, selection, exam_date, verbose=False):
    "Build PNG files from selection of questions"

    # Load config
    config = toml.load(_config_path_local / _config)

    # Iterate over questions
    for key in selection:
        tex = ""

        # Add header
        with open(_dir_config / _snapshot) as f:
            header = f.read()
            tex += header

        # Add question
        part, number, index = key
        question, answer, solution = questions[key]
        tex += "\\begin{minipage}{12cm}\n"
        tex += question + "\n"
        tex += "\\end{minipage}\n"

        # Add footer
        with open(_dir_config / _footer) as f:
            footer = f.read()
            tex += footer

        # Set file names
        prefix = "%s_%d_%d" % (part, number, index)
        tex_file = prefix + ".tex"
        pdf_file = prefix + ".pdf"
        png_file = prefix + ".png"

        # Write TeX to file
        with open(_dir_tmp / tex_file, "w") as f:
            f.write(tex)

        # Build PDF and PNG
        os.chdir(_dir_tmp)
        subprocess.run(["pdflatex", tex_file], capture_output=(not verbose))
        subprocess.run(
            ["convert", "-density", "600", pdf_file, png_file],
            capture_output=(not verbose),
        )
        os.chdir("..")

        # Copy PNG file to snapshot directory
        png_dir = exam_prefix(exam_date, config["code"], config["_exam"])
        if not os.path.exists(_dir_png / png_dir):
            os.mkdir(_dir_png / png_dir)
        shutil.copy(_dir_tmp / png_file, _dir_png / png_dir)
        print(f"Snapshot written to {_dir_png / png_dir / png_file}")


def help():
    print("Usage: make-exam <exam date>")


def main():
    print(f"This is TentaMaker, version {_version}\n")

    # Check if exam has been initialized
    if not os.path.exists(_config_path_local / "pool.tex"):
        print("Exam has not been initialized. Run 'init-exam' first.")
        return

    # Parse command-line arguments
    if len(sys.argv) < 2:
        help()
        sys.exit(1)
    exam_date = sys.argv[1]
    randomize = "--randomize" in sys.argv
    verbose = "--verbose" in sys.argv
    snapshots = "--no-snapshots" not in sys.argv

    # Load questions from pool
    questions = load_questions()

    # Create selection of questions
    selection = create_selection(questions, randomize)

    # Build PDF files
    build_pdf(questions, selection, exam_date, True, verbose)
    build_pdf(questions, selection, exam_date, False, verbose)

    # Build PNG files (snapshots)
    if snapshots:
        build_png(questions, selection, exam_date, verbose=verbose)
