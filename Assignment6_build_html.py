# CSCI 355/655
# Summer 2022
# Assignment 3 - Scraping, HTML, and CSS
# Weixin Yang


import webbrowser
import os
import requests
import pymysql

from bs4 import BeautifulSoup

TAG_DOCTYPE = '<!DOCTYPE html>'
TAG_HTML = 'html'
TAG_HEAD = 'head'
TAG_BODY = 'body'
TAG_TABLE = 'table'
TAG_A = 'a'
TAG_TH = 'th'
TAG_TD = 'td'
TAG_TR = 'tr'
TAG_PAR = 'p'
TAG_H1 = 'h1'  # HTML supports six default heading tags H1, H2, H3, H4, H5, and H6
TAG_BR = 'br'
TAG_LINK = 'link'

def read_password():
    with open("password.txt") as file:
        password = file.read().strip()
    return password

def connect_to_mars():
    password = read_password()
    conn = pymysql.connect(host="mars.cs.qc.cuny.edu", port=3306, user="yawe8598", passwd=password, database="yawe8598")
    # cursor = conn.cursor()
    # cursor.execute("SHOW DATABASES")
    # for row in cursor:
    #     print(row)
    return conn

def get_state_data():
    url = 'https://www.thespreadsheetguru.com/blog/list-united-states-capitals-abbreviations'
    # get URL html
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    data = []
    items = soup.find_all('p')


    capitol_data = ""
    abbvr_data = ""

    for item in items:
        if "Alabama" in item:
            state_data = str(item)
        if "NJ" in item:
            abbvr_data = str(item)
        if "Juneau" in item:
            capitol_data = str(item)
    #print(f"test_data = {test_data}")

    index = state_data.index("Alabama")
    state_data = state_data[index:].split("<br/>")

   # print(state_data)

    index = abbvr_data.index("AL")
    abbvr_data = abbvr_data[index:].split("<br/>")
    #print(abbvr_data)

    index = capitol_data.index("Montgomery")
    capitol_data  = capitol_data[index:].split("<br/>")
    #print(capitol_data)
    state_data[49] = state_data[49].replace('</p>', '')
    abbvr_data[49] = abbvr_data[49].replace('</p>', '')
    capitol_data[49] = capitol_data[49].replace('</p>', '')
    states = []
    for i in range(50):
        states.append([state_data[i], abbvr_data[i], capitol_data[i]] )

    return states


def insert_state_data(states):
    conn = connect_to_mars()
    cursor = conn.cursor()
    for state in states:
        query = "insert into state values ('"+state[1]+"','"+state[0]+"','"+state[2]+"')"
        print(query)
        cursor.execute(query)
    conn.commit()
    conn.close()


def write_file(file_name, message):
    f = open(file_name, 'w')
    f.write(message)
    f.close()


def create_element(tag, content, attributes="", end_tag=True):
    element = "<" + tag + " " + attributes + ">"
    if end_tag:
        element += content + "</" + tag + ">"
    return element + "\n"


def create_elements(tag, list_contents):
    elements = ""
    for content in list_contents:
        elements += create_element(tag, content)
    return elements


def create_table(headers, data):
    rows = create_elements(TAG_TH, headers)
    for datum in data:
        name = datum[0]
        href = 'href="https://en.wikipedia.org/wiki/' + name.replace(" ", "_") + '_(state)' + '"'
        a = create_element(TAG_A, name, href, True)
        tda = create_element(TAG_TD, a)
        tds = create_elements(TAG_TD, datum[1:])
        row = create_element(TAG_TR, tda + tds)
        rows += row
    table = create_element(TAG_TABLE, rows)
    return table


def get_state_data_from_db():


    conn = connect_to_mars()
    cursor = conn.cursor()
    query = "SELECT * FROM state ORDER BY state_name"
    cursor.execute(query)
    rows = cursor.fetchall()
    print(cursor.rowcount)
    states = []
    for row in rows:
        states += [row]
        print(row)
    return states



def open_file_in_browser(filename):
    url = 'file:///' + os.getcwd() + '/' + filename
    webbrowser.open_new_tab(url)


def main():
    states = get_state_data_from_db()
    headers = ["State", "Abbreviation", "Capital"]
    table = create_table(headers, states)
    head = create_element(TAG_HEAD, '')
    heading = create_element(TAG_H1, "Weixin's United States Data from Database, yawe8598")
    link_attributes = 'rel="stylesheet" href = "myStyle.css"'
    link = create_element(TAG_LINK, "", link_attributes, end_tag=False)
    head = create_element(TAG_HEAD, link)
    body = create_element(TAG_BODY, heading + table)
    message = create_element(TAG_HTML, head + body)
    write_file("states.html", message)
    open_file_in_browser("states.html")



if __name__ == "__main__":
    main()
