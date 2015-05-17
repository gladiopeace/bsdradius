# BSDRadius #

BSDRadius is open source RADIUS server targeted for use in Voice over IP (VoIP) applications. While there are quite large number of Radius servers (including free) available in the world, little number of them (if any) are developed with !VoIP specific needs in mind. Typical !VoIP RADIUS server should be able to take high amount of AAA requests in short time periods, handle large databases, and respond timely to prevent time-outs and request retransmission cases. Most commonly used VoIP protocols (SIP and H.323) use small number of Authentication methods (e.g. CHAP and Digest), and this can allow reduce processing overhead and code size of server.

The server is released under the BSD license, which means that you are allowed to download, install, use and modify it at no charge.

## Get the code ##
To use the latest and greatest code of BSDRadius - use Subversion with command:
` svn checkout https://bsdradius.googlecode.com/svn/trunk/ bsdradius `