from tdom import html, Node


def Heading(name: str) -> Node:
    return html(t'<div>Hello {name}</div>')


if __name__ == '__main__':
    print(html(t'<{Heading} name="World"/><div>Refactor Me</div>'))
