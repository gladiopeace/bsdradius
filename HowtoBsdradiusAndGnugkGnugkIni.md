
```
[Gatekeeper::Main]
Fourtytwo=42
Name=gnugk
TimeTolive=600
UnicastRasPort=1719
MulticastPort=1718
EndpointSignalPort=1720
ListenQueueLength=1024
SignalReadTimeout=2000
StatusReadTimeout=3000

[RoutedMode]
GKRouted=1
H245Routed=1
CallSignalPort=1720
CallSignalHandlerNumber=4
AcceptNeighborsCalls=1
AcceptUnregisteredCalls=1
RemoveH245AddressOnTunneling=1
RemoveCallOnDRQ=0
DropCallsByReleaseComplete=1
SendReleaseCompleteOnDRQ=1
SupportNATedEndpoints=1
ForwardOnFacility=1
Q931PortRange=20000-20999
H245PortRange=30000-30999
SignalTimeout=25000
AlertingTimeout=25000

[Proxy]
Enable=0
T120PortRange=0
RTPPortRange=1024-65535
ProxyForNAT=1
ProxyForSameNAT=1

[GKStatus::Auth]
Rule=explicit | regex
127.0.0.1=allow
Default=forbid

[RasSrv::GWPrefixes]
all=*

[RasSrv::PermanentEndpoints]
10.1.1.2=all;

[CallTable]
GenerateUCCDR=TRUE
DefaultCallTimeout=7200  // 2hr
GenerateNBCDR=0

[Gatekeeper::Auth]
; registered endpoints should be authenticated by H.235 password using RadAuth
; unregistered calls cannot be accepted
RadAliasAuth=required;ARQ,RRQ,SetupUnreg
;RadAliasAuth=required;SetupUnreg

[RadAliasAuth]
Servers=127.0.0.1
LocalInterface=127.0.0.1
DefaultAuthPort=1812
SharedSecret=gktest123
RequestTimeout=3500
IdCacheTimeout=9000
SocketDeleteTimeout=60000
RequestRetransmissions=2
AppendCiscoAttributes=1
IncludeEndpointIP=1
UseDialedNumber=1

[RadAuth]
Servers=127.0.0.1
LocalInterface=127.0.0.1
DefaultAuthPort=1812
SharedSecret=gktest123
RequestTimeout=5000
IdCacheTimeout=9000
SocketDeleteTimeout=60000
RequestRetransmissions=2
AppendCiscoAttributes=1
IncludeEndpointIP=1
UseDialedNumber=1

[Gatekeeper::Acct]
RadAcct=required;start,stop,update,on,off

[RadAcct]
Servers=127.0.0.1
LocalInterface=127.0.0.1
DefaultAcctPort=1813
SharedSecret=gktest123
RequestTimeout=5000
IdCacheTimeout=9000
SocketDeleteTimeout=60000
RequestRetransmissions=4
AppendCiscoAttributes=1
UseDialedNumber=1
```