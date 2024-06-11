def create_bibtex(refstring):
    # Hier die Funktion einfügen. Input und Output sind jeweils Strings

    out_string = refstring [::-1]
    out_string = out_string.upper()

    out_string = '''@article{lname:year,
            author  = "lname, fname",
            title   = "title",
            journal = "journal",
            year    = "year",
            volume  = "volume",
            number  = "number",
            pages   = "p--pp"
    }'''

    return out_string


# Hier können auch die Hilfsfunktionen hin

