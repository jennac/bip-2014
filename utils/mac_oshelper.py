def no_hidden(self, dirs):
    return [d if not d[0]=='.' for d in dirs]
