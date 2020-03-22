import unittest
from mock import mock
from parameterized import parameterized

from conans.test.utils.conanfile import MockConanfile, MockSettings
from conans.client.tools import OSInfo
from conans.errors import ConanInvalidConfiguration, ConanException

from conans.tools import check_max_cppstd, valid_max_cppstd


class CheckMaxCppStdTests(unittest.TestCase):

    def test_user_inputs(self):
        """ Inputs with incorrect types should throw ConanException
        """
        conanfile = MockConanfile(MockSettings({}))

        with self.assertRaises(ConanException) as raises:
            check_max_cppstd("conanfile", "17", False)
        self.assertEqual("conanfile parameter must be an instance of ConanFile",
                         str(raises.exception))

        with self.assertRaises(ConanException) as raises:
            check_max_cppstd(conanfile, "gnu17", False)
        self.assertEqual("cppstd parameter must be a number", str(raises.exception))

        with self.assertRaises(ConanException) as raises:
            check_max_cppstd(conanfile, 17, "False")
        self.assertEqual("gnu_extensions parameter must be a bool", str(raises.exception))

    def _create_conanfile(self, compiler, version, os, cppstd, libcxx=None):
        settings = MockSettings({"arch": "x86_64",
                                 "build_type": "Debug",
                                 "os": os,
                                 "compiler": compiler,
                                 "compiler.version": version,
                                 "compiler.cppstd": cppstd})
        if libcxx:
            settings.values["compiler.libcxx"] = libcxx
        conanfile = MockConanfile(settings)
        return conanfile

    @parameterized.expand(["98", "11", "14", "17"])
    def test_check_max_cppstd_from_settings(self, cppstd):
        """ check_max_cppstd must accept cppstd higher/equal than cppstd in settings
        """
        conanfile = self._create_conanfile("gcc", "9", "Linux", "98", "libstdc++")
        check_max_cppstd(conanfile, cppstd, False)

    @parameterized.expand(["11", "14", "17"])
    def test_check_max_cppstd_from_newer_settings(self, cppstd):
        """ check_max_cppstd must raise when cppstd is greater when supported on settings
        """
        conanfile = self._create_conanfile("gcc", "9", "Linux", cppstd, "libstdc++")
        with self.assertRaises(ConanInvalidConfiguration) as raises:
            check_max_cppstd(conanfile, "98", False)
        self.assertEqual("Current cppstd ({}) is higher than the required C++ standard "
                         "(98).".format(cppstd), str(raises.exception))

    @parameterized.expand(["98", "11", "14", "17"])
    def test_check_max_cppstd_from_settings_with_extension(self, cppstd):
        """ current cppstd in settings must has GNU extension when extensions is enabled
        """
        conanfile = self._create_conanfile("gcc", "9", "Linux", "gnu98", "libstdc++")
        check_max_cppstd(conanfile, cppstd, True)

        conanfile.settings.values["compiler.cppstd"] = "98"
        with self.assertRaises(ConanException) as raises:
            check_max_cppstd(conanfile, cppstd, True)
        self.assertEqual("The cppstd GNU extension is required", str(raises.exception))

    def test_check_max_cppstd_supported_default_standard(self):
        """ check_max_cppstd should not raise when compiler supports a standard by default
        """
        conanfile = self._create_conanfile("gcc", "9", "Linux", None, "libstdc++")
        check_max_cppstd(conanfile, "42", False)

    def test_check_max_cppstd_unsupported_default_standard(self):
        """ check_max_cppstd must raise when compiler does not support a standard by default
        """
        conanfile = self._create_conanfile("gcc", "9", "Linux", None, "libstdc++")

        with self.assertRaises(ConanInvalidConfiguration) as raises:
            check_max_cppstd(conanfile, "11", False)
        self.assertEqual("Current cppstd (gnu14) is higher than the required C++ standard (11).",
                         str(raises.exception))

    def test_check_max_cppstd_gnu_compiler_extension(self):
        """ Current compiler must support GNU extension on Linux when extensions is required
        """
        conanfile = self._create_conanfile("gcc", "9", "Linux", None, "libstdc++")
        with mock.patch("platform.system", mock.MagicMock(return_value="Linux")):
            with mock.patch.object(OSInfo, '_get_linux_distro_info'):
                with mock.patch("conans.client.tools.settings.cppstd_default", return_value="17"):
                    with self.assertRaises(ConanException) as raises:
                        check_max_cppstd(conanfile, "17", True)
                    self.assertEqual("The cppstd GNU extension is required", str(raises.exception))

    def test_no_compiler_declared(self):
        conanfile = self._create_conanfile(None, None, "Linux", None, "libstdc++")
        with self.assertRaises(ConanException) as raises:
            check_max_cppstd(conanfile, "14", False)
        self.assertIn("compiler is not specified", str(raises.exception))

    def test_unknown_compiler_declared(self):
        conanfile = self._create_conanfile("sun-cc", "5.13", "Linux", None, "libstdc++")
        with self.assertRaises(ConanInvalidConfiguration) as raises:
            check_max_cppstd(conanfile, "14", False)
        self.assertEqual("Could not detect default cppstd for "
                         "the current compiler.", str(raises.exception))


class ValidMaxCppstdTests(unittest.TestCase):

    def test_user_inputs(self):
        """ Inputs with incorrect types should throw ConanException
        """
        conanfile = MockConanfile(MockSettings({}))

        with self.assertRaises(ConanException) as raises:
            valid_max_cppstd("conanfile", "17", False)
        self.assertEqual("conanfile parameter must be an instance of ConanFile",
                         str(raises.exception))

        with self.assertRaises(ConanException) as raises:
            valid_max_cppstd(conanfile, "gnu17", False)
        self.assertEqual("cppstd parameter must be a number", str(raises.exception))

        with self.assertRaises(ConanException) as raises:
            valid_max_cppstd(conanfile, 17, "False")
        self.assertEqual("gnu_extensions parameter must be a bool", str(raises.exception))

    def _create_conanfile(self, compiler, version, os, cppstd, libcxx=None):
        settings = MockSettings({"arch": "x86_64",
                                 "build_type": "Debug",
                                 "os": os,
                                 "compiler": compiler,
                                 "compiler.version": version,
                                 "compiler.cppstd": cppstd})
        if libcxx:
            settings.values["compiler.libcxx"] = libcxx
        conanfile = MockConanfile(settings)
        return conanfile

    @parameterized.expand(["98", "11", "14", "17"])
    def test_valid_max_cppstd_from_settings(self, cppstd):
        """ valid_max_cppstd must accept cppstd higher/equal than cppstd in settings
        """
        conanfile = self._create_conanfile("gcc", "9", "Linux", "98", "libstdc++")
        self.assertTrue(valid_max_cppstd(conanfile, cppstd, False))

    @parameterized.expand(["11", "14", "17"])
    def test_valid_max_cppstd_from_newer_settings(self, cppstd):
        """ valid_max_cppstd returns False when cppstd is greater when supported on settings
        """
        conanfile = self._create_conanfile("gcc", "9", "Linux", cppstd, "libstdc++")
        self.assertFalse(valid_max_cppstd(conanfile, "98", False))

    @parameterized.expand(["98", "11", "14", "17"])
    def test_valid_max_cppstd_from_settings_with_extension(self, cppstd):
        """ valid_max_cppstd must return True when current cppstd in settings has GNU extension and
            extensions is enabled
        """
        conanfile = self._create_conanfile("gcc", "9", "Linux", "gnu98", "libstdc++")
        self.assertTrue(valid_max_cppstd(conanfile, cppstd, True))

        conanfile.settings.values["compiler.cppstd"] = "98"
        self.assertFalse(valid_max_cppstd(conanfile, cppstd, True))

    def test_valid_max_cppstd_supported_default_standard(self):
        """ valid_max_cppstd must return True when compiler supports a standard by default
        """
        conanfile = self._create_conanfile("gcc", "9", "Linux", None, "libstdc++")
        self.assertTrue(valid_max_cppstd(conanfile, "42", False))

    def test_valid_max_cppstd_unsupported_default_standard(self):
        """ valid_max_cppstd must return False when compiler does not support a standard by default
        """
        conanfile = self._create_conanfile("gcc", "9", "Linux", None, "libstdc++")
        self.assertFalse(valid_max_cppstd(conanfile, "11", False))

    def test_valid_max_cppstd_gnu_compiler_extension(self):
        """ valid_max_cppstd must return False when current compiler does not support GNU extension
            on Linux and extensions is required
        """
        conanfile = self._create_conanfile("gcc", "9", "Linux", None, "libstdc++")
        with mock.patch("platform.system", mock.MagicMock(return_value="Linux")):
            with mock.patch.object(OSInfo, '_get_linux_distro_info'):
                with mock.patch("conans.client.tools.settings.cppstd_default", return_value="gnu20"):
                    self.assertFalse(valid_max_cppstd(conanfile, "11", True))

    @parameterized.expand(["98", "11", "14", "17"])
    def test_max_cppstd_mingw_windows(self, cppstd):
        """ GNU extensions HAS effect on Windows when running a cross-building for Linux
        """
        with mock.patch("platform.system", mock.MagicMock(return_value="Windows")):
            conanfile = self._create_conanfile("gcc", "9", "Linux", "gnu98", "libstdc++")
            self.assertTrue(valid_max_cppstd(conanfile, cppstd, True))

            conanfile.settings.values["compiler.cppstd"] = "98"
            self.assertFalse(valid_max_cppstd(conanfile, cppstd, True))
