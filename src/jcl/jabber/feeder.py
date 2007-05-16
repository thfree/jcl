# -*- coding: UTF-8 -*-
##
## component.py
## Login : David Rousselie <dax@happycoders.org>
## Started on  Wed Aug  9 21:04:42 2006 David Rousselie
## $Id$
## 
## Copyright (C) 2006 David Rousselie
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##

"""FeederComponent with default Feeder and Sender
implementation"""

__revision__ = "$Id: feeder.py,v 1.3 2005/09/18 20:24:07 dax Exp $"

import logging

from jcl.jabber.component import JCLComponent
from jcl.lang import Lang
from jcl.model.account import Account

from pyxmpp.message import Message

class FeederComponent(JCLComponent):
    """Implement a feeder sender behavior based on the
    regular interval behavior of JCLComponent
    feed data from given Feeder and send it to user
    through the given Sender."""
    def __init__(self,
                 jid,
                 secret,
                 server,
                 port,
                 db_connection_str,
                 lang = Lang()):
        JCLComponent.__init__(self, \
                              jid, \
                              secret, \
                              server, \
                              port, \
                              db_connection_str, \
                              lang = lang)
        # Define default feeder and sender, can be override
        self.feeder = Feeder(self)
        self.sender = Sender(self)
        self.check_interval = 1

        self.__logger = logging.getLogger("jcl.jabber.FeederComponent")
        
    def handle_tick(self):
        """Implement main feed/send behavior"""
        self.db_connect()
        for _account in Account.select(clauseTables = ["account"], \
                                       orderBy = "user_jid"):
            for subject, body in self.feeder.feed(_account):
                self.sender.send(_account, subject, body)
        self.db_disconnect()



class Feeder(object):
    """Abstract feeder class"""
    def __init__(self, component = None):
        self.component = component

    def feed(self, _account):
        """Feed data for given account"""
        raise NotImplementedError


class Sender(object):
    """Abstract sender class"""
    def __init__(self, component = None):
        self.component = component

    def send(self, to_account, subject, body):
        """Send data (subject and body) to given account"""
        raise NotImplementedError

class MessageSender(Sender):
    """Send data as Jabber Message"""

    def send(self, to_account, subject, body):
        """Implement abstract method from Sender class and send data as Jabber message"""
        self.component.stream.send(Message(\
                    from_jid = to_account.jid, \
                    to_jid = to_account.user_jid, \
                    subject = subject, \
                    stanza_type = "normal", \
                    body = body))

class HeadlineSender(Sender):
    """Send data as Jabber Headline"""

    def send(self, to_account, subject, body):
        """Implement abstract method from Sender class and send data as Jabber headline"""
        self.component.stream.send(Message(\
                    from_jid = to_account.jid, \
                    to_jid = to_account.user_jid, \
                    subject = subject, \
                    stanza_type = "headline", \
                    body = body))
