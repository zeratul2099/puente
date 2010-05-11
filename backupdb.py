#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
import settings

os.system("echo '%s' | gpg -es -u 'Pünte OSS' --passphrase-fd 0 --yes -r 'Pünte OSS' %s"%(settings.PASSPHRASE, settings.DATABASE_NAME))
os.system("ncftpput 134.106.143.8 /upload/software/ %s.gpg"%(settings.DATABASE_NAME))

