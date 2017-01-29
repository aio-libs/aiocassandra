import invoke

# Based on https://github.com/pyca/cryptography/blob/master/tasks.py


@invoke.task
def release(version):
    invoke.run('git tag -a aiocassandra-{0} -m "aiocassandra {0} release"'.format(version))  # noqa
    invoke.run('git push --tags')

    invoke.run('python setup.py sdist')
    invoke.run('twine upload -r pypi dist/aiocassandra-{0}*'.format(version))
