# -*- coding: utf-8 -*-

import argparse
import os
import pydoc
import re
import subprocess
import sys
import uuid
import webbrowser
from builtins import input

from django.utils.termcolors import colorize

import requests
from six import string_types


def r(msg):
    return colorize(msg, fg="red")


def g(msg):
    return colorize(msg, fg="green")


def y(msg):
    return colorize(msg, fg="yellow")


def b(msg):
    return colorize(msg, opts=('bold',))


def o(cmd, msg=None, shell=False, timeout=None):
    if shell:
        assert isinstance(cmd, string_types), "with shell, cmd must be string"
    else:
        if isinstance(cmd, string_types):
            cmd = cmd.split()

    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=shell,
        cwd=os.getcwd(), stdin=subprocess.DEVNULL,
    )
    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        print("timeout, cmd=%s" % (cmd))

    if msg and (proc.returncode or proc.returncode is None):
        print(r(msg))

    if proc.returncode is None:
        print("setting returncode to 128")
        proc.returncode = 128

    return proc.stdout.read().decode("utf-8"), proc.returncode


def must(cmd, msg=None, shell=False, timeout=None):
    op, code = o(cmd, shell=shell, timeout=timeout)
    if code:
        if msg:
            print(r(msg))
            print(op)
            sys.exit(code)

        raise Exception(
            "Command failed with non zero exit code [%s:%s]\n%s" % (cmd, code, op)
        )
    return op


def gh_token():
    return open(os.path.expanduser("~/.github")).read().strip().split(":")[1]


def gh_login():
    return open(os.path.expanduser("~/.github")).read().strip().split(":")[0]


def gh_post_json(url, data):
    url = "https://api.github.com/repos/amitu/worddb/" + url
    return requests.post(url, params={"access_token": gh_token()}, json=data)


def gh_api(url, params=None):
    if params is None:
        params = {}

    params["access_token"] = gh_token()
    url = "https://api.github.com/repos/amitu/worddb/" + url
    return requests.get(url, params=params)


def gh_update_pr(id, **data):
    r = requests.patch(
        "https://api.github.com/repos/amitu/worddb/issues/%d" % id,
        params={
            "access_token": gh_token(),
        },
        json=data,
    )
    if r.status_code != 200:
        print(r.status_code)
        print(r.text)
    return r


def has_local_changes():
    return bool(o("git diff --quiet")[1])


def has_unpushed_changes():
    branch = current_branch()
    return bool(must("git log origin/%s..%s" % (branch, branch)).strip())


def random_branch_name():
    return str(uuid.uuid4()).replace("-", "")


def current_branch():
    return must(
        "git rev-parse --symbolic-full-name --abbrev-ref HEAD", "Not a git repo?"
    ).strip()


def wrap(msg):
    return "\n".join(
        '\n'.join(line.strip() for line in re.findall(r'.{1,70}(?:\s+|$)', x))
        for x in msg.splitlines()
    )


def author_title(pr):
    author, title = pr["title"].split("] ", 1)
    return author[1:], title


def handle_list(args):
    print(y("Getting PR data."))
    prs = gh_api("pulls").json()
    branch = current_branch()
    current = None
    you = gh_login()

    if branch != "master":
        for pr in prs:
            if pr["head"]["ref"] == current_branch():
                author, title = author_title(pr)
                if author != gh_login():
                    title = "[%s] %s" % (r(author), title)
                if pr["assignee"]:
                    print(
                        "%s [%s -> %s]: %s" % (
                            b("Current"),
                            g("#%s" % pr["number"]),
                            pr["assignee"]["login"],
                            title,
                        )
                    )
                else:
                    print(
                        "%s [%s]: %s" % (
                            b("Current"), g("#%s" % pr["number"]), title
                        )
                    )
                current = pr
                break
        else:
            print("No pull request for %s." % r(branch))

    yours = []
    review_pending = []
    rest = []

    for pr in prs:
        author, title = author_title(pr)
        if pr == current:
            continue

        if author == you:
            yours.append(pr)
            continue

        if pr["assignee"] and pr["assignee"]["login"] == you:
            review_pending.append(pr)
            continue

        rest.append(pr)

    if yours:
        print()
        print(b("Yours:"))
        for pr in reversed(yours):
            _, title = author_title(pr)
            if pr["assignee"]:
                print(
                    "%s [%s]: %s" % (
                        g("#%s" % pr["number"]),
                        pr["assignee"]["login"],
                        title,
                    )
                )
            else:
                print("%s: %s" % (g("#%s" % pr["number"]), title))

    if review_pending:
        print()
        print(b("Your review needed:"))
        for pr in reversed(review_pending):
            author, title = author_title(pr)
            print(
                "%s [%s]: %s" % (
                    g("#%s" % pr["number"]),
                    r(author),
                    title,
                )
            )

    if rest:
        print()
        print(b("Others:"))
        for pr in reversed(rest):
            author, title = author_title(pr)
            if pr["assignee"]:
                print(
                    "%s [%s -> %s]: %s" % (
                        g("#%s" % pr["number"]),
                        r(author),
                        pr["assignee"]["login"],
                        title,
                    )
                )
            else:
                print(
                    "%s [%s]: %s" % (g("#%s" % pr["number"]), r(author), title)
                )


def handle_show(args):
    print(y("Fetching from origin."))
    must("git fetch origin --prune")
    print(y("Getting PR data."))
    pr = gh_api("pulls/%d" % args.id).json()
    message = "Author: %s\n" % pr["user"]["login"]
    message += "Title: %s\n\n" % g(pr["title"])
    message += wrap(pr["body"] or r("No body."))
    diff, _ = o(
        "git --no-pager diff origin/master...origin/%s --color" % (
            pr["head"]["ref"]
        ), timeout=2,
    )
    message += "\n\n\n%s" % diff
    pydoc.pager(message)
    return pr, message


def handle_approve(args):
    if has_local_changes():
        print(r("Can not perform this operation with local changes."))
        return

    pr, message = handle_show(args)
    current = current_branch()
    branch = pr["head"]["ref"]
    _, title = author_title(pr)
    description = pr["body"] or ""
    description += (
        "\n\nPR: https://github.com/amitu/worddb/pull/%s" % args.id
    )
    description = wrap(description)

    while True:
        try:
            resp = input(
                "Do you want to merge? [%sHOW AGAIN/%spen/%ses/%so]: " % (
                    g("S"), g("o"), g("y"), g("n")
                )
            ).lower()
            if resp == "open" or resp == "o":
                handle_open(args)
                return
            if resp == "yes" or resp == "y":
                break
            if resp == "" or resp == "show again" or resp == "s":
                pydoc.pager(message)
                continue
            return
        except KeyboardInterrupt:
            return

    must("git checkout %s" % branch)
    print(y("Pulling origin."))
    must("git pull origin %s" % branch)
    must("git rebase origin/master")
    must(["git", "commit", "--amend", "-m", "%s\n\n%s" % (title, description)])
    print(y("Pushing origin"))
    must("git push origin %s --force" % branch)
    must("git checkout master")
    must("git merge origin/master")
    must("git rebase origin/%s" % branch)
    must("git branch -d %s" % branch)
    must("git push origin master :%s" % branch)

    if current != branch:
        must("git checkout %s" % current)

    print("Approved %s." % g("#%s: %s" % (args.id, title)))


def handle_comment(args):
    gh_post_json(
        "issues/%d/comments" % args.id, {"body": args.comment}
    ).json()
    print(g("Posted comment."))


def handle_open(args):
    webbrowser.open("https://github.com/amitu/worddb/pull/%d" % args.id)


def handle_switch(args):
    if has_local_changes():
        print(r("Has local changes, can't switch."))
        return

    print(y("Fetching upstream changes."))
    o("git fetch origin --prune", "Could not fetch, check internet/permissions.")

    print(y("Getting PR info from Github."))
    pr = gh_api("pulls/%d" % args.id).json()

    if pr["state"] != "open":
        print(r("Can not switch to non open PR [state=%s]." % pr["state"]))
        return

    if current_branch() == pr["head"]["ref"]:
        print(r("You are already on #%s." % args.id))
        return

    must("git checkout %s" % pr["head"]["ref"])
    print("Switched to: %s" % g("[#%d] %s" % (pr["number"], pr["title"])))


def last_commit_author():
    return must("git log -1").split("\n")[1]


def handle_commit(args):
    print(y("Fetching upstream changes."))
    o("git fetch origin --prune", "Could not fetch, check internet/permissions.")

    if not has_local_changes():
        print("No local changes.")
        must("git rebase origin/master")
        print(y("Pushing upstream."))
        must("git push -f", "Could not push, push manually.")
        return

    if args.preserve_author:
        must("git commit --amend -am wip")
        must("git rebase origin/master")  # can conflict, resolve it,
        print(y("Pushing upstream."))
        must("git push -f")
        print(g("Add done."))
        return

    oauthor = last_commit_author()

    must("git commit --amend --reset-author -am wip")
    must("git rebase origin/master")  # can conflict, resolve it,
    print(y("Pushing upstream."))
    must("git push -f")

    if oauthor == last_commit_author():
        return

    print(r("Committer changed, updating pull request."))
    # to get PR number and current title for this branch. since we do not
    # know the PR number either, we have to fetch full PR list, and match
    print(y("Fetching PRs"))
    branch = current_branch()
    for pr in gh_api("pulls").json():
        if pr["head"]["ref"] != branch:
            continue
        break
    else:
        print(r("Failed. No PR open for this branch [%s]!" % branch))
        return
    _, title = author_title(pr)
    title = "[%s] %s" % (gh_login(), title)
    if title != pr["title"]:
        print(y("Updating PR"))
        gh_update_pr(pr["number"], title=title)
    print(g("Add done."))


def handle_assign(args):
    pr = gh_update_pr(args.id, assignee=args.who).json()
    print(
        "Assigned %s to %s." % (
            g("[#%s] %s" % (pr["number"], pr["title"])),
            r(pr["assignee"]["login"]),
        )
    )


def handle_mm(args):
    if has_local_changes():
        print(r("Can not merge with local changes."))
        return

    print(y("Fetching latest changes."))
    must("git fetch origin --prune")
    must("git rebase origin/master")
    print(y("Pushing changes to origin."))
    must("git push -f")
    print(g("Merged."))


def handle_unassign(args):
    print(y("Unassigning."))
    pr = gh_update_pr(args.id, assignee='').json()
    print("Unassigned %s." % g("[#%s] %s" % (pr["number"], pr["title"])))


def handle_start(args):
    if current_branch() != "master":
        print(r("Start from master branch only."))
        return

    print(y("Fetching lastest master."))
    o("git fetch origin --prune", "Could not fetch, check internet/permissions.")
    branch = random_branch_name()
    print(y("Creating branch: %s." % branch))
    must("git checkout -b %s" % branch)
    print(y("Pushing branch to GitHub."))

    must("git commit -am wip --allow-empty")
    must("git push --set-upstream origin %s" % branch)

    print("Creating pull request.")

    if not args.who:
        args.who = gh_login()
    title = "[%s] %s" % (args.who, args.title)
    url = must(["hub", "pull-request", "-m", title]).strip()

    print(g(url))


def handle_diff(args):
    d1 = must("git diff --color")
    d2 = must("git diff --cached --color")
    d3 = must("git diff origin/master.. --color", shell=True)
    msg = g("Unstaged changes:") + "\n\n" + d1 + "\n\n"
    msg += g("Staged changes:") + "\n\n" + d2 + "\n\n"
    msg += g("Committed changes:") + "\n\n" + d3

    pydoc.pager(msg)


def forbidden_on_master(func):
    return func in [handle_assign, handle_commit, handle_diff, handle_mm]


def main():
    parser = argparse.ArgumentParser(
        prog='gg', description="Git wrapper to work using acko workflow."
    )
    subparsers = parser.add_subparsers()

    parser_list = subparsers.add_parser('list', help='list open tasks')
    parser_list.set_defaults(func=handle_list)

    parser_show = subparsers.add_parser('show', help='show details of a task')
    parser_show.add_argument("id", help="task id", type=int)
    parser_show.set_defaults(func=handle_show)

    parser_approve = subparsers.add_parser('approve', help='approve a task')
    parser_approve.add_argument("id", help="task id", type=int)
    parser_approve.set_defaults(func=handle_approve)

    parser_comment = subparsers.add_parser('comment', help='comment on a task')
    parser_comment.add_argument("id", help="task id", type=int)
    parser_comment.add_argument("comment", help="comment", type=str)
    parser_comment.set_defaults(func=handle_comment)

    paerser_open = subparsers.add_parser('open', help='browse task on github')
    paerser_open.add_argument("id", help="task id", type=int)
    paerser_open.set_defaults(func=handle_open)

    parser_switch = subparsers.add_parser('switch', help='switch task')
    parser_switch.add_argument("id", help="task id", type=int)
    parser_switch.set_defaults(func=handle_switch)

    parser_commit = subparsers.add_parser('commit', help='commit current task')
    parser_commit.add_argument(
        "-p", "--preserve-author",
        help="Preserve authorship",
        action="store_true",
    )
    parser_commit.set_defaults(func=handle_commit)

    parser_assign = subparsers.add_parser(
        'assign', help='assign a task for review'
    )
    parser_assign.add_argument("id", help="task id", type=int)
    parser_assign.add_argument("who", help="who to assign to", type=str)
    parser_assign.set_defaults(func=handle_assign)

    parser_unassign = subparsers.add_parser(
        'unassign', help='unassign a task for review'
    )
    parser_unassign.add_argument("id", help="task id", type=int)
    parser_unassign.set_defaults(func=handle_unassign)

    parser_start = subparsers.add_parser('start', help='create a new task')
    parser_start.add_argument("title", help="title of the task", type=str)
    parser_start.add_argument("--who", help="assign this task to", type=str)
    parser_start.set_defaults(func=handle_start)

    parser_diff = subparsers.add_parser('diff', help='show diff of current task')
    parser_diff.set_defaults(func=handle_diff)

    parser_mm = subparsers.add_parser(
        'mm', help='rebase on latest master from origin'
    )
    parser_mm.set_defaults(func=handle_mm)

    args = parser.parse_args()

    if forbidden_on_master(args.func) and current_branch() == "master":
        print(r("Can not do this operation on master."))

    args.func(args)


"""
Which color library to use? Options are:

1. from django.utils.termcolors import colorize
2. https://pypi.python.org/pypi/termcolor
3. https://pypi.python.org/pypi/colorama
4. https://pypi.python.org/pypi/blessings/
5. https://github.com/kennethreitz/clint
6. https://pypi.python.org/pypi/colorprint/0.1
7. https://pypi.python.org/pypi/colorconsole
8. https://github.com/Robpol86/colorclass

We are going with django, as django is already our dependency.
"""

if __name__ == '__main__':
    main()
