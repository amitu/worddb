PROJDIR=`dirname $0`

alias gg=gg
unalias gg

0() {
    cd $PROJDIR
}

run0() {
    manage runserver
}

migrate() {
    pushd $PROJDIR/src/dj > /dev/null
    python manage.py migrate
    popd > /dev/null
}

makemigrations() {
    pushd $PROJDIR/src/dj > /dev/null
    python manage.py makemigrations $1
    popd > /dev/null
}

djshell() {
    pushd $PROJDIR/src/dj > /dev/null
    python manage.py shell
    popd > /dev/null
}

dbshell() {
    pushd $PROJDIR/src/dj > /dev/null
    python manage.py dbshell
    popd > /dev/null
}

createsuperuser() {
    pushd $PROJDIR/src/dj > /dev/null
    python manage.py createsuperuser
    popd > /dev/null
}

manage() {
    pushd $PROJDIR/src/dj > /dev/null
    python manage.py $*
    popd > /dev/null
}

loaddata() {
    pushd $PROJDIR/src/dj > /dev/null
    python manage.py loaddata
    popd > /dev/null
}

recreatedb() {
    psql -c "DROP DATABASE IF EXISTS worddb;" template1
    psql -c "CREATE DATABASE worddb" template1
    psql -c "CREATE EXTENSION IF NOT EXISTS hstore;" worddb
    migrate
}

gg() {
    python gg.py $*
}
