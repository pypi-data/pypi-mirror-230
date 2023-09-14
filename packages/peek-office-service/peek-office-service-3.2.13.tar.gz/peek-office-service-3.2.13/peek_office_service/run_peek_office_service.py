#!/usr/bin/env python
"""
 * synnova.py
 *
 *  Copyright Synerty Pty Ltd 2013
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by
 *  Synerty Pty Ltd
 *
"""
from peek_platform.util.LogUtil import (
    setupPeekLogger,
    updatePeekLoggerHandlers,
    setupLoggingToSyslogServer,
)
from peek_platform.util.ManHoleUtil import start_manhole
from peek_plugin_base.PeekVortexUtil import peekOfficeName, peekServerName
from pytmpdir.dir_setting import DirSetting
from txhttputil.site.FileUploadRequest import FileUploadRequest
from txhttputil.site.SiteUtil import setupSite
from vortex.DeferUtil import vortexLogFailure
from vortex.VortexFactory import VortexFactory

setupPeekLogger(peekOfficeName)

from twisted.internet import reactor, defer

import logging

# EXAMPLE LOGGING CONFIG
# Hide messages from vortex
# logging.getLogger('txhttputil.vortex.VortexClient').setLevel(logging.INFO)

# logging.getLogger('peek_office_service_pof.realtime.RealtimePollerEcomProtocol'
#                   ).setLevel(logging.INFO)

logger = logging.getLogger(__name__)


def setupPlatform():
    from peek_platform import PeekPlatformConfig

    PeekPlatformConfig.componentName = peekOfficeName

    # Tell the platform classes about our instance of the PluginSwInstallManager
    from peek_office_service.sw_install.PluginSwInstallManager import (
        PluginSwInstallManager,
    )

    PeekPlatformConfig.pluginSwInstallManager = PluginSwInstallManager()

    # Tell the platform classes about our instance of the PeekSwInstallManager
    from peek_office_service.sw_install.PeekSwInstallManager import (
        PeekSwInstallManager,
    )

    PeekPlatformConfig.peekSwInstallManager = PeekSwInstallManager()

    # Tell the platform classes about our instance of the PeekLoaderBase
    from peek_office_service.plugin.ClientPluginLoader import ClientPluginLoader

    PeekPlatformConfig.pluginLoader = ClientPluginLoader()

    # The config depends on the componentName, order is important
    from peek_office_service.PeekClientConfig import PeekClientConfig

    PeekPlatformConfig.config = PeekClientConfig()

    # Update the version in the config file
    from peek_office_service import __version__

    PeekPlatformConfig.config.platformVersion = __version__

    # Set default logging level
    logging.root.setLevel(PeekPlatformConfig.config.loggingLevel)
    updatePeekLoggerHandlers(
        PeekPlatformConfig.componentName,
        PeekPlatformConfig.config.daysToKeep,
        PeekPlatformConfig.config.logToStdout,
    )

    if PeekPlatformConfig.config.loggingLogToSyslogHost:
        setupLoggingToSyslogServer(
            PeekPlatformConfig.config.loggingLogToSyslogHost,
            PeekPlatformConfig.config.loggingLogToSyslogPort,
            PeekPlatformConfig.config.loggingLogToSyslogFacility,
        )

    # Enable deferred debugging if DEBUG is on.
    if logging.root.level == logging.DEBUG:
        defer.setDebugging(True)

    # If we need to enable memory debugging, turn that on.
    if PeekPlatformConfig.config.loggingDebugMemoryMask:
        from peek_platform.util.MemUtil import setupMemoryDebugging

        setupMemoryDebugging(
            PeekPlatformConfig.componentName,
            PeekPlatformConfig.config.loggingDebugMemoryMask,
        )

    # Set the reactor thread count
    reactor.suggestThreadPoolSize(
        PeekPlatformConfig.config.twistedThreadPoolSize
    )

    # Initialise the txhttputil Directory object
    DirSetting.defaultDirChmod = PeekPlatformConfig.config.DEFAULT_DIR_CHMOD
    DirSetting.tmpDirPath = PeekPlatformConfig.config.tmpPath
    FileUploadRequest.tmpFilePath = PeekPlatformConfig.config.tmpPath

    # Setup manhole
    if PeekPlatformConfig.config.manholeEnabled:
        start_manhole(
            PeekPlatformConfig.config.manholePort,
            PeekPlatformConfig.config.manholePassword,
            PeekPlatformConfig.config.manholePublicKeyFile,
            PeekPlatformConfig.config.manholePrivateKeyFile,
        )


def main():
    # defer.setDebugging(True)
    # sys.argv.remove(DEBUG_ARG)
    # import pydevd
    # pydevd.settrace(suspend=False)

    setupPlatform()

    # Import remaining components
    from peek_office_service import importPackages

    importPackages()

    # Make the agent restart when the server restarts, or when it looses connection
    def restart(status):
        from peek_platform import PeekPlatformConfig

        PeekPlatformConfig.peekSwInstallManager.restartProcess()

    def setupVortexOfflineSubscriber():
        (
            VortexFactory.subscribeToVortexStatusChange(peekServerName)
            .filter(lambda online: online == False)
            .subscribe(on_next=restart)
        )

    # First, setup the VortexServer Agent
    from peek_platform import PeekPlatformConfig

    d = VortexFactory.createTcpClient(
        PeekPlatformConfig.componentName,
        PeekPlatformConfig.config.peekServerHost,
        PeekPlatformConfig.config.peekServerVortexTcpPort,
    )

    # Start Update Handler,
    # Add both, The peek client might fail to connect, and if it does, the payload
    # sent from the peekSwUpdater will be queued and sent when it does connect.

    # Software update check is not a thing any more
    # d.addErrback(vortexLogFailure, logger, consumeError=True)
    # d.addCallback(lambda _: peekSwVersionPollHandler.start())

    # Start client main data observer, this is not used by the plugins
    # (Initialised now, not as a callback)

    # Load all Plugins
    d.addErrback(vortexLogFailure, logger, consumeError=True)
    d.addCallback(lambda _: PeekPlatformConfig.pluginLoader.loadCorePlugins())
    d.addCallback(
        lambda _: PeekPlatformConfig.pluginLoader.loadOptionalPlugins()
    )

    d.addCallback(lambda _: PeekPlatformConfig.pluginLoader.startCorePlugins())
    d.addCallback(
        lambda _: PeekPlatformConfig.pluginLoader.startOptionalPlugins()
    )

    # Set this up after the plugins have loaded, it causes problems with the ng build
    d.addCallback(lambda _: setupVortexOfflineSubscriber())

    def startSite(_):
        from peek_office_service.backend.SiteRootResource import (
            setupOffice,
            officeRoot,
        )

        setupOffice()

        # Create the desktop vortex server
        officeHttpServer = PeekPlatformConfig.config.officeHttpServer
        setupSite(
            "Peek Office Site",
            officeRoot,
            portNum=officeHttpServer.sitePort,
            enableLogin=False,
            redirectFromHttpPort=officeHttpServer.redirectFromHttpPort,
            sslBundleFilePath=officeHttpServer.sslBundleFilePath,
        )

    d.addCallback(startSite)

    def startedSuccessfully(_):
        logger.info(
            "Peek Office is running, version=%s",
            PeekPlatformConfig.config.platformVersion,
        )
        return _

    d.addErrback(vortexLogFailure, logger, consumeError=True)
    d.addCallback(startedSuccessfully)

    reactor.addSystemEventTrigger(
        "before",
        "shutdown",
        PeekPlatformConfig.pluginLoader.stopOptionalPlugins,
    )
    reactor.addSystemEventTrigger(
        "before", "shutdown", PeekPlatformConfig.pluginLoader.stopCorePlugins
    )

    reactor.addSystemEventTrigger(
        "before",
        "shutdown",
        PeekPlatformConfig.pluginLoader.unloadOptionalPlugins,
    )
    reactor.addSystemEventTrigger(
        "before", "shutdown", PeekPlatformConfig.pluginLoader.unloadCorePlugins
    )

    reactor.addSystemEventTrigger("before", "shutdown", VortexFactory.shutdown)

    reactor.run()


if __name__ == "__main__":
    main()
