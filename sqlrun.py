from fyCursor import connect

cur = connect('database.db')

while (True):
    in_ = input(">>")
    cur.execute(in_).commit()

    print(cur.execute(in_).fetch())

    if input(">") == 0:
        break
