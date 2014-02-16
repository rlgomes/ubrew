
import tempfile
import subprocess
import os

from parameterizedtestcase import ParameterizedTestCase

class CmdLine(object):

    def __init__(self, shell="bash"):
        # by printing a new line we 
        print('')
        self.shell = shell
        self.tempdir = tempfile.mktemp()
        os.makedirs(self.tempdir)
   
    def run(self, command):
        """
        runs a shell script that is verified to return 0 otherwise this method
        throws an exception
        """

        proc = subprocess.Popen([self.shell],
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        proc.stdin.write(('. scripts/ubrew.sh\n').encode('utf-8'))
        proc.stdin.write(('export UBREW_PACKAGES=testapps\n').encode('utf-8'))
        proc.stdin.write(('export HOME=%s\n' % self.tempdir).encode('utf-8'))

        for line in command.split('\n'):
            print('> %s' % line)
            proc.stdin.write(('%s\n' % line).encode('utf-8'))
        
        # Not a fan of this but there's no other way of getting the ENV 
        # and saving the previous return code so we can correctly return it
        proc.stdin.write(('RC=$?; env > ENV; exit $RC\n').encode('utf-8'))

        output, error = proc.communicate()

        output = output.decode('utf-8')
        error = error.decode('utf-8')

        # read the env back into memory
        try:
            envfile = open('ENV','r')
            lines = envfile.read()
            env = {}
            for line in lines.split('\n'):
                if line.strip() == '':
                    continue

                splits = line.split('=')
                env[splits[0]] = splits[1]

            envfile.close()
            os.remove('ENV')
        except:
            for line in output.split('\n'):
                print('OUT: %s' % line)

            for line in error.split('\n'):
                print('ERR: %s' % line)

            raise

        return proc.returncode, env, output, error


def assertResult(exit_code, stdout, stderr, expected_exit_code=None):

    if expected_exit_code:
        if exit_code != expected_exit_code:

            for line in stdout.split('\n'):
                print('OUT: %s' % line)

            for line in stderr.split('\n'):
                print('ERR: %s' % line)

            raise AssertionError("unexpected return code %s, expecting %s" % \
                                 (exit_code, expected_exit_code))


_PARAMS = [
           ('makeapp','bash'),
           ('prebuiltapp','bash'),

           ('makeapp','zsh'),
           ('prebuiltapp','zsh'),

           ('makeapp','sh'),
           ('prebuiltapp','sh'),

           ('makeapp','dash'),
           ('prebuiltapp','dash'),
          ]

class BasicTests(ParameterizedTestCase):


    @ParameterizedTestCase.parameterize(("app", "shell"), _PARAMS)
    def test_available(self, app, shell):
        cli = CmdLine(shell=shell)

        exit_code, _, stdout, stderr = cli.run("ubrew available %s" % app)
        assertResult(exit_code, stdout, stderr, expected_exit_code = 0)
    
        for version in range(1, 5):
            self.assertTrue(('%s.0' % version) in stdout)


    @ParameterizedTestCase.parameterize(("app", "shell"), _PARAMS)
    def test_install_v1_0(self, app, shell):
        cli = CmdLine(shell = shell)
        exit_code, _, stdout, stderr = cli.run("ubrew install %s 1.0" % app)
        assertResult(exit_code, stdout, stderr, expected_exit_code = 0)


    @ParameterizedTestCase.parameterize(("app", "shell"), _PARAMS)
    def test_install_invalid_version(self, app, shell):
        cli = CmdLine(shell=shell)
        exit_code, _, stdout, stderr = cli.run("ubrew install %s 5.0" % app)
        assertResult(exit_code, stdout, stderr, expected_exit_code = 1)


    @ParameterizedTestCase.parameterize(("app", "shell"), _PARAMS)
    def test_install_version_with_bad_url(self, app, shell):
        cli = CmdLine(shell=shell)
        exit_code, _, stdout, stderr = cli.run("ubrew install %s 4.0" % app)
        assertResult(exit_code, stdout, stderr, expected_exit_code = 1)


    @ParameterizedTestCase.parameterize(("app", "shell"), _PARAMS)
    def test_install_use_v1_0(self, app, shell):
        cli = CmdLine(shell=shell)

        exit_code, _, stdout, stderr = cli.run("ubrew install %s 1.0" % app)
        assertResult(exit_code, stdout, stderr, expected_exit_code = 0)

        exit_code, env, stdout, stderr = cli.run("ubrew use %s 1.0" % app)
        assertResult(exit_code, stdout, stderr, expected_exit_code = 0)
        self.assertTrue(('%s/1.0' % app) in env['PATH'],
                        msg='PATH contains %s' % env['PATH'])


    @ParameterizedTestCase.parameterize(("app", "shell"), _PARAMS)
    def test_install_use_v1_0_verify_with_active(self, app, shell):
        cli = CmdLine(shell=shell)

        exit_code, _, stdout, stderr = cli.run("ubrew install %s 1.0" % app)
        assertResult(exit_code, stdout, stderr, expected_exit_code = 0)

        exit_code, env, stdout, stderr = cli.run("ubrew use %s 1.0" % app)
        assertResult(exit_code, stdout, stderr, expected_exit_code = 0)

        exit_code, env, stdout, stderr = cli.run("""
ubrew use %s 1.0
ubrew active %s
""" % (app, app))
        assertResult(exit_code, stdout, stderr, expected_exit_code = 0)
        self.assertTrue(('%s-1.0 is active' % app) in stdout, '%s' % stdout)


    @ParameterizedTestCase.parameterize(("app", "shell"), _PARAMS)
    def test_install_v1_0_verify_not_active(self, app, shell):
        cli = CmdLine(shell=shell)

        exit_code, _, stdout, stderr = cli.run("ubrew install %s 1.0" % app)
        assertResult(exit_code, stdout, stderr, expected_exit_code = 0)

        exit_code, env, stdout, stderr = cli.run("ubrew active %s" % app)
        assertResult(exit_code, stdout, stderr, expected_exit_code = 1)
        self.assertTrue(('%s no active version' % app) in stdout, '%s' % stdout)

 
    @ParameterizedTestCase.parameterize(("app", "shell"), _PARAMS)
    def test_uninstall_version_that_wasnt_installed(self, app, shell):
        cli = CmdLine(shell=shell)

        exit_code, _, stdout, stderr = cli.run("ubrew uninstall %s 1.0" % app)
        assertResult(exit_code, stdout, stderr, expected_exit_code = 1)


    @ParameterizedTestCase.parameterize(("app", "shell"), _PARAMS)
    def test_install_uninstall_verify_use_fails(self, app, shell):
        cli = CmdLine(shell=shell)

        exit_code, _, stdout, stderr = cli.run("ubrew install %s 1.0" % app)
        assertResult(exit_code, stdout, stderr, expected_exit_code = 0)

        exit_code, _, stdout, stderr = cli.run("ubrew uninstall %s 1.0" % app)
        assertResult(exit_code, stdout, stderr, expected_exit_code = 0)

        exit_code, _, stdout, stderr = cli.run("ubrew use %s 1.0" % app)
        assertResult(exit_code, stdout, stderr, expected_exit_code = 1)


    @ParameterizedTestCase.parameterize(("app", "shell"), _PARAMS)
    def test_install_multiple_versions_and_verify_installed(self, app, shell):
        cli = CmdLine(shell=shell)

        exit_code, _, stdout, stderr = cli.run("ubrew install %s 1.0" % app)
        assertResult(exit_code, stdout, stderr, expected_exit_code = 0)

        exit_code, _, stdout, stderr = cli.run("ubrew install %s 2.0" % app)
        assertResult(exit_code, stdout, stderr, expected_exit_code = 0)

        exit_code, _, stdout, stderr = cli.run("ubrew installed %s" % app)
        assertResult(exit_code, stdout, stderr, expected_exit_code = 0)
        self.assertTrue('1.0' in stdout)
        self.assertTrue('2.0' in stdout)


    @ParameterizedTestCase.parameterize(("app", "shell"), _PARAMS)
    def test_use_v2_0_after_v1_0_deactivates_v1_0(self, app, shell):
        cli = CmdLine(shell=shell)

        exit_code, _, stdout, stderr = cli.run("ubrew install %s 1.0" % app)
        assertResult(exit_code, stdout, stderr, expected_exit_code = 0)

        exit_code, _, stdout, stderr = cli.run("ubrew install %s 2.0" % app)
        assertResult(exit_code, stdout, stderr, expected_exit_code = 0)

        exit_code, env, stdout, stderr = cli.run("ubrew use %s 1.0" % app)
        assertResult(exit_code, stdout, stderr, expected_exit_code = 0)
        self.assertTrue(('%s/1.0' % app) in env['PATH'])

        exit_code, env, stdout, stderr = cli.run("ubrew use %s 2.0" % app)
        assertResult(exit_code, stdout, stderr, expected_exit_code = 0)
        self.assertTrue(('%s/2.0' % app) in env['PATH'])
        self.assertTrue(('%s/1.0' % app) not in env['PATH'])


    @ParameterizedTestCase.parameterize(("app", "shell"), _PARAMS)
    def test_use_version_that_wasnt_installed(self, app, shell):
        cli = CmdLine(shell=shell)

        exit_code, _, stdout, stderr = cli.run("ubrew use %s 1.0" % app)
        assertResult(exit_code, stdout, stderr, expected_exit_code = 1)


