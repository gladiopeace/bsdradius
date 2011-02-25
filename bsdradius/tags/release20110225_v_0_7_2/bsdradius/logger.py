## BSDRadius is released under BSD license.
## Copyright (c) 2006, DATA TECH LABS
## All rights reserved. 
## 
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met: 
## * Redistributions of source code must retain the above copyright notice,
##   this list of conditions and the following disclaimer. 
## * Redistributions in binary form must reproduce the above copyright notice,
##   this list of conditions and the following disclaimer in the documentation
##   and/or other materials provided with the distribution. 
## * Neither the name of the DATA TECH LABS nor the names of its contributors
##   may be used to endorse or promote products derived from this software without
##   specific prior written permission. 
## 
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
## ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
## ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# HeadURL		$HeadURL: file:///Z:/backup/svn/bsdradius/branches/v_0_7/bsdradius/logger.py $
# Author:		$Author: valts $
# File version:	$Revision: 289 $
# Last changes:	$Date: 2006-12-28 17:47:41 +0200 (Ce, 28 Dec 2006) $

import bsdradius.webstuff.logger as lgg
import sys

# HACK!!! HACK!!! HACK!!!
# let's use webstuff's logger module instead of this one.
# I suggest you all to make fast search&replace job in all BSDRadius modules
# replace bsdradius.logger with webstuff.logger everywhere

sys.modules['logger'] = lgg
sys.modules['bsdradius.logger'] = lgg
