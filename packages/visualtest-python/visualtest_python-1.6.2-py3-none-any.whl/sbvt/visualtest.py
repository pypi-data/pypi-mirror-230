import json
import os
import logging
import time
from packaging import version as semver

import requests
import sbvt
from colorama import Fore
from colorama import Style

from .browser import Browser
from .imagetools import ImageTools
from .api import Api
from colorama import Fore, Style

log = logging.getLogger(f'vt.{os.path.basename(__file__)}')

class VisualTest:
    """
    Class for SmartBear VisualTest

    Args:
        driver: Selenium webdriver with active session
        settings: Dictionary of user settings
            - projectToken (str): Unique API token for your project. (required)
            - testRunName (str): Test Run Name - defaults to OS / Browser versions if not provided (optional)
            - saveTo (str): The directory to which images should be saved. (default is your working directory/results/)
        settings: Dictionary of developer settings
            - debug (bool): 
                Creates sbvt_debug folder with log file
                Keeps temp folder of images used to build fullpage screenshots
                Saves DOM JSON file
        limits: Dictionary of values to change default limits during creation fullpage images (not recommended)
            - MAX_IMAGE_PIXELS (int): Max fullpage image size. (default INT32 or 2^31)
            - MAX_TIME_MIN (float): Max time to create fullpage image.  Default is 3.5 minutes. Can be set to a max of 10 minutes. 
    Returns:
        Class instance
    """

    def __init__(self, driver, settings: dict={}, limits: dict={}):

        if not driver:
            raise Exception('driver argument is required!')

        if not driver.session_id:
            raise Exception('driver argument does not have a session_id!')

        if not driver.capabilities:
            raise Exception('driver argument does not have capabilities!')
        
        # must do this first to get debug logs
        self._debug = False
        self._debugDir = None
        if 'debug' in settings:
            if (type(settings['debug']) == bool):
                if (settings['debug']):
                    self._debug = True
                    subfolder = time.strftime("%m-%d_%H-%M-%S", time.localtime()) + "_" + driver.session_id
                    self._debugDir = os.path.join('sbvt_debug',  subfolder)
                    os.makedirs(self._debugDir, exist_ok=True)
                    self._startLogger(self._debugDir)
            else:
                raise Exception('debug argument must be a boolean')

        log.info(f'Instantiated with settings: {settings}, limits: {limits}')
        
        try:
            response = requests.get(f'https://pypi.org/pypi/visualtest-python/json', timeout=5)
            latest_version = response.json()['info']['version']
            log.info(f'Running visualtest-python v{sbvt.__version__}. latest: v{latest_version}')
            if (semver.Version(sbvt.__version__) < semver.Version(latest_version)):
                print(f'{Fore.YELLOW}WARNING: A newer version of visualtest-python SDK is available. Your version {sbvt.__version__}. Latest version {latest_version}. Consider upgrading with "pip install visualtest-python --upgrade"{Style.RESET_ALL}')
        except:
            log.info('Failed getting visualtest-python version from pypi.org in 5 seconds... continuing')

        if 'projectToken' in settings:
            if '_' in settings['projectToken']:
                projectToken = settings['projectToken']
                env = projectToken.split('_')[1]
            else:
                env = "prod"
            Api.setEnv(env)

        self._settings = {
            'projectToken': None,
            'testRunName': None,
            'saveTo': None
        }

        # user-configurable project information
        if not 'projectToken' in settings:
            raise Exception('"projectToken" property in settings is required!')
        self._settings['projectToken'] = settings['projectToken']

        # setup api
        self._api = Api(self._settings['projectToken'])

        self._api.canConnectToApiServer()
        self._api.isValidProjectToken()

        self.browser = Browser(driver, limits)
        self.browser.debug =  self._debug
        self.browser.debugDir =  self._debugDir
        self._sessionId = driver.session_id
        
        if 'testRunName' in settings:
            if(len(settings['testRunName']) > 100):
                raise Exception(f'The maximum size of testRunName is 100 characters. {len(settings["testRunName"])} characters given.')
            self._settings['testRunName'] = settings['testRunName']
        else:
            if self.browser._deviceInfo["osName"] == 'macos':
                osNamePretty = 'macOS'
            else:
                osNamePretty = self.browser._deviceInfo["osName"].capitalize()
            self._settings['testRunName'] = f'{osNamePretty} {self.browser._deviceInfo["osVersion"]} / {self.browser._deviceInfo["browserName"].capitalize()} {self.browser._deviceInfo["browserVersion"]}'

        if 'saveTo' in settings:
            self.saveTo = os.path.join(settings['saveTo'])

        if 'debug' in settings and type(settings['debug']) == bool:
            self.browser.debug = settings['debug']

        if "testRunId" in settings:
            if isinstance(settings['testRunId'], str):
                self._api.testRun = {'testRunId': settings['testRunId']}
            else:
                raise Exception('"testRunId" should be a str type.')
        
        log.info(f'final instance settings: {self._settings}')

    @property
    def projectToken(self):
        """
        Get projectToken (str)
        """
        return self._settings['projectToken']

    @property
    def saveTo(self):
        """
        Get/Set save directory path for screenshot results (str)
            - will create directories if path does not exist
        """
        return self._settings['saveTo']

    @saveTo.setter
    def saveTo(self, path):
        if type(path) == str:
            if not os.path.exists(path):
                tokens = os.path.split(path)
                try: 
                    os.makedirs(path)
                    self._settings['saveTo'] = path
                    log.info(f'Created new directory at {str(path)}')
                except Exception as e:
                    raise Exception(f'Error creating directory {str(path)}: {str(e)}')
            else:
                log.info(f'Directory already existed at: {path}')
                self._settings['saveTo'] = path
        else:
            raise Exception(f'Argument must be a string!')

    @property
    def scrollMethod(self):
        """
        Get/Set scrolling method for fullpage screenshots
        
        Args:
            method: name of scrolling method
                - CSS_TRANSLATE: default/recommended
                    - shifts the page up while capturing images but does not actually scroll the page
                - JS_SCROLL: not recommended
                    - uses Javascript to scroll the browser while capture images

        """
        return self.browser.scrollMethod

    @scrollMethod.setter
    def scrollMethod(self, method):
        self.browser.scrollMethod = method

    @property
    def capabilities(self):
        """
        Read-only access to selenium webdriver capabilities (dict)
        """
        return self.browser.capabilities

    @property
    def deviceInfo(self):
        """
        Read-only access to device info (dict)
        """
        return self.browser._deviceInfo

    @property
    def MAX_IMAGE_PIXELS(self):
        """
        Get/Set the maximum number of image pixels allowed for fullpage screenshot (int)
        """
        return ImageTools.getMaxImagePixels()

    @MAX_IMAGE_PIXELS.setter
    def MAX_IMAGE_PIXELS(self, pixels):
        ImageTools.setMaxImagePixels(pixels)

    @property
    def MAX_TIME_MIN(self):
        """
        Get/Set the current maximum number of minutes a fullpage screenshot is allowed to run before it stops scrolling (float)
        """
        return self.browser.MAX_TIME_MIN

    @MAX_TIME_MIN.setter
    def MAX_TIME_MIN(self, minutes):
        self.browser.MAX_TIME_MIN = minutes

    def _startLogger(self, logPath):
        logger = logging.getLogger('vt')
        formatter = logging.Formatter('%(asctime)s [%(name)s][%(levelname)s] %(message)s')
        fileHandler = logging.FileHandler(os.path.join(logPath, 'debug.log'), mode='w')
        fileHandler.setFormatter(formatter)
        logger.addHandler(fileHandler)
        logger.setLevel(logging.DEBUG)

    def capture(self, name, options: dict={}):
        """
        Capture a screenshot from the browser under test
        
        Args:
            name: the unique name used both in naming the file, and identifying the visual test image 
            options: dictionary
                - { 'element': WebElement }: value must be a selenium webdriver element and will take an element screenshot
                - { 'vieport': true }: will capture an image of the browser's current viewport
                - if neither 'element', nor 'viewport' provided, defaults to capture a fullpage screenshot
                - { 'lazyload': 1000 }: For fullpage screenshot, will load lazy content before capturing screenshot
                - { 'ignoreElements': ['.css-selector'] }: For any screenshot, will specify elements to ignore during image comparison
        
        Returns:
            Information about the screenshot result
        """
        if not name:
            raise Exception(f'Name argument is required')

        if type(name) != str:
            raise Exception(f'Name argument must be a string')

        if len(name) > 100:
            raise Exception(f'Name argument cannot be greater than 100 characters')

        imageType = None

        self.browser._clearIgnoreElements() #clear the window from previous ignoredElements
        if 'ignoreElements' in options:
            if not isinstance(options['ignoreElements'], list):
                raise Exception(f'ignoreElements must be of type "list"')
            if not all(isinstance(item, str) for item in options['ignoreElements']):
                raise Exception(f'ignoreElements values must all be strings')
            
            elementsNotFound = []
            for cssSelector in options['ignoreElements']:
                try:
                    self.browser._findElement(cssSelector)
                except:
                    elementsNotFound.append(cssSelector)
            
            if len(elementsNotFound) > 0:
                raise Exception(f'Some ignoreElements were not found on the page: {",".join(elementsNotFound)}')
            else:
                self.browser._injectIgnoreElements(options['ignoreElements'])

        if 'freezePage' in options:
            if not isinstance(options['freezePage'], bool):
                raise Exception(f'freezePage must be of type "bool"')

        comparisonMode = None
        sensitivity = None
        if 'comparisonMode' in options:
            if not isinstance(options['comparisonMode'], str):
                raise Exception(f'comparisonMode must be of type "str"')
            if options['comparisonMode'] == 'detailed':
                comparisonMode = 'detailed'
            elif options['comparisonMode'] == 'layout':
                comparisonMode = 'layout'
                if 'sensitivity' in options:
                    if not isinstance(options['sensitivity'], str):
                        raise Exception(f'sensitivity must be of type "str"')
                    if options['sensitivity'] in ['low', 'medium', 'high']:
                        if options['sensitivity'].__eq__('low'):
                            sensitivity = 0
                        elif options['sensitivity'].__eq__('medium'):
                            sensitivity = 1
                        elif options['sensitivity'].__eq__('high'):
                            sensitivity = 2
                    else:
                        raise Exception(f'sensitivity value should be "low", "medium" or "high".')
                else:
                    raise Exception(f'sensitivity value should be set to "low", "medium" or "high" when passing comparisonMode="layout".')
            else:
                raise Exception(f'comparisonMode value should be "detailed" or "layout" mode.')

        if 'element' in options:
            screenshotResult = self.browser.takeElementScreenshot(options)
            imageType = 'element'
        elif 'viewport' in options and options['viewport'] == True:

            screenshotResult = self.browser.takeViewportScreenshot(options)
            imageType = 'viewport'
        else:
            if 'lazyload' in options:
                if type(options['lazyload']) != int or options['lazyload'] < 0 or options['lazyload'] > 10000:
                    raise Exception('"lazyload" value must be an integer between 0 and 10000 ms!')

            screenshotResult = self.browser.takeFullpageScreenshot(name, options)

            imageType = 'fullpage'
        
        
         # save final image to debug file
        if self._debug:
            fileDir = os.path.join(self._debugDir, f'{name}-{imageType}')
            os.makedirs(fileDir, exist_ok=True)
            imagePath = os.path.join(fileDir, f'{name}.png')
            domPath = os.path.join(fileDir, f'{name}.json')

            with open(imagePath, 'wb') as outfile:
                outfile.write(screenshotResult['imageBinary'])
                outfile.close()
            with open(domPath, 'w') as outfile:
                json.dump(self.browser.dom, outfile, indent=4)

        # save final image to saveTo location
        if self.saveTo is not None:
            current_time = time.strftime('%H-%M-%S', time.localtime())
            saveToFile = os.path.join(self._settings['saveTo'], f'{name}-{imageType}_{current_time}.png')
            screenshotResult['imagePath'] = saveToFile
            with open(saveToFile, 'wb') as outfile:
                outfile.write(screenshotResult['imageBinary'])
                outfile.close()
        
        
        # save image to server
        imageData = {
            'sessionId': self._sessionId,
            'imageName': name,
            'imageType': imageType,
            'imageExt': 'png',
            'testUrl': self.browser._driver.current_url,
            'viewportWidth': self.browser.viewportWidth,
            'viewportHeight': self.browser.viewportHeight,
            'imageWidth': screenshotResult['imageSize']['width'],
            'imageHeight': screenshotResult['imageSize']['height'],
            'ignoredElements': json.dumps(self.browser.dom['ignoredElementsData']),
            'comparisonMode': comparisonMode,
            'sensitivity': sensitivity,
            'headless': self.browser._headless,
            'sdkDomUpload': True # SDKs will upload dom to S3 directly and receive presigned URL if this flag is set
        }
        imageData.update(self.browser._deviceInfo) # required information about device/os/browser

        # these two are informational and just used to store - not required
        imageData.update({'driverCapabilities': json.dumps(self.browser.capabilities)})
        imageData.update({'userAgentInfo': json.dumps(self.browser._userAgentInfo)})

        # post the image, creating testrun if new
        imageApiResult = self._api.saveImage(self._settings['testRunName'], imageData, screenshotResult['imageBinary'], json.dumps(self.browser.dom))

        # do not return the binary to the results
        del screenshotResult['imageBinary']

        return {
            'screenshotResult': screenshotResult,
            'imageApiResult': imageApiResult,
        }

    def printReport(self):
        
        comparisons = self._api.getTestRunResult()
        imageCount = comparisons["total"]
        print(f'View your {imageCount} {"capture" if imageCount == 1 else "captures"} here: ' + Fore.BLUE + self._api.testRun['appUrl'] + Style.RESET_ALL)

        try:
            # print(f'Comparisons: {str(comparisons)}')
            new = comparisons["status"]["new_image"]
            failed = comparisons["status"]["unreviewed"]
            passed = comparisons["status"]["passed"]

            if new:
                print(Style.BRIGHT + Fore.YELLOW + f'\t{new} new base {"image" if new == 1 else "images"}' + Style.RESET_ALL)
            if failed:
                print(Style.BRIGHT + Fore.RED + f'\t{failed} image comparison {"failure" if failed == 1 else "failures"} to review' + Style.RESET_ALL)
            if passed:
                print(Style.RESET_ALL + Style.BRIGHT + Fore.GREEN + f'\t{passed} image comparisons passed' + Style.RESET_ALL)
            if comparisons["complete"] != imageCount:
                print(Style.BRIGHT + Fore.MAGENTA + f'\tTimed out getting comparisons results' + Style.RESET_ALL)
        except Exception as e:
            print(Style.BRIGHT + Fore.MAGENTA + f'\tError getting comparisons results: {str(e)}' + Style.RESET_ALL)

    def getTestRunResult(self):
        comparisons = self._api.getTestRunResult()
        return {
            'passed' : comparisons['aggregate']['passed'], 
            'failed' : comparisons['aggregate']['failed']
            }

    def setDeviceName(self, deviceName):
        if(type(deviceName) == str ):
            self.browser._deviceInfo["deviceName"] = deviceName
        else:
            raise Exception('"deviceName" should be a str type.')
        
    def getDeviceName(self):
        return self.browser._deviceInfo["deviceName"]