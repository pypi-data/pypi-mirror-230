"""LiveFlow class.
"""
# Copyright (c) LiveAction, Inc. 2022. All rights reserved.
# Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
# Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

import json
from typing import Union

from .invariant import EngineOperation as EO
from .omnierror import OmniError
from .helpers import (
    load_native_props_from_list, load_props_from_dict, OmniScriptEncoder, repr_array, str_array)


_wan_mac_item_list = [
    'ifidx',
    'ifname'
]

_wan_mac_item_dict = {
    'mac': 'ethernet_address'
}


class WanMacItem(object):
    """The WanMacItem class has the attributes of a
    LiveFlow router map entry.
    """

    if_index = 1
    """The ifindex of an adapter."""

    if_name = ''
    """The interface name of an adapter."""

    ethernet_address = ''
    """The Ethernet Address of an adapter."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'WanMacItem({{'
            f'if_index: {self.if_index}, '
            f'if_name: "{self.if_name}", '
            f'ethernet_address: "{self.ethernet_address}"'
            f'}})'
        )

    def __str__(self):
        return (
            f'Wan Mac Item: '
            f'if_index={self.if_index}, '
            f'if_name="{self.if_name}", '
            f'ethernet_address="{self.ethernet_address}"'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_native_props_from_list(self, props, _wan_mac_item_list)
        load_props_from_dict(self, props, _wan_mac_item_dict)


_ipfix_prop_list = [
    'active_flow_refresh_interval',
    'avc_enabled',
    'flowdir_enabled',
    'fnf_enabled',
    'max_payload',
    'medianet_enabled',
    'options_template_refresh_interval',
    'signaling_dn_enabled',
    'template_refresh_interval',
    'target_address'
]


class Ipfix(object):
    """The Ipfix class has the attributes of LiveFlow IPFIX preferences."""

    active_flow_refresh_interval = 60
    """Indicates the time interval (in seconds) in which LiveFlow generates data records."""

    avc_enabled = True
    """Whether LiveFlow should generate AVC IPFIX records."""

    flowdir_enabled = True
    """Indicates whether the flowDirection key is sent in unidirectional IPFIX records indicating
    the flow direction: 0 = ingress, 1 = egress.
    """

    fnf_enabled = True
    """Whether LiveFlow should generate FNF IPFIX records."""

    max_payload = 1500
    """The MTU of IPFIX packets."""

    medianet_enabled = True
    """Whether LiveFlow should generate MediaNet IPFIX records."""

    options_template_refresh_interval = 600
    """Indicates the time interval (in seconds) in which LiveFlow generates IPFIX option template
    records.
    """

    signaling_dn_enabled = True
    """Whether LiveFlow should generate Signaling DN IPFIX records."""

    template_refresh_interval = 600
    """Indicates the time interval (in seconds) in which LiveFlow generates IPFIX template
    records."""

    target_address = '127.0.0.1'
    """Indicates the location of the server instance receiving IPFIX records from LiveFlow:
    Option #1: An IP address,
    Option #2: An IP address and port in the following form: ip_address:port.
    """

    wan_mac_list = []
    """The LiveFlow router mappings."""

    def __init__(self, props):
        self.active_flow_refresh_interval = Ipfix.active_flow_refresh_interval
        self.avc_enabled = Ipfix.avc_enabled
        self.flowdir_enabled = Ipfix.flowdir_enabled
        self.fnf_enabled = Ipfix.fnf_enabled
        self.max_payload = Ipfix.max_payload
        self.medianet_enabled = Ipfix.medianet_enabled
        self.options_template_refresh_interval = Ipfix.options_template_refresh_interval
        self.signaling_dn_enabled = Ipfix.signaling_dn_enabled
        self.template_refresh_interval = Ipfix.template_refresh_interval
        self.target_address = Ipfix.target_address
        self._load(props)

    def __repr__(self):
        return (
            f'Ipfix({{'
            f'active_flow_refresh_interval: {self.active_flow_refresh_interval}, '
            f'avc_enabled: {self.avc_enabled}, '
            f'flowdir_enabled: {self.flowdir_enabled}, '
            f'fnf_enabled: {self.fnf_enabled}, '
            f'max_payload: {self.max_payload}, '
            f'medianet_enabled: {self.medianet_enabled}, '
            f'options_template_refresh_interval: {self.options_template_refresh_interval}, '
            f'signaling_dn_enabled: {self.signaling_dn_enabled}, '
            f'template_refresh_interval: {self.template_refresh_interval}, '
            f'target_address: "{self.target_address}", '
            f'wan_mac_list: [{repr_array(self.wan_mac_list)}]'
            f'}})'
        )

    def __str__(self):
        return (
            f'Ipfix: '
            f'active_flow_refresh_interval={self.active_flow_refresh_interval}, '
            f'avc_enabled={self.avc_enabled}, '
            f'flowdir_enabled={self.flowdir_enabled}, '
            f'fnf_enabled={self.fnf_enabled}, '
            f'max_payload={self.max_payload}, '
            f'medianet_enabled={self.medianet_enabled}, '
            f'options_template_refresh_interval={self.options_template_refresh_interval}, '
            f'signaling_dn_enabled={self.signaling_dn_enabled}, '
            f'template_refresh_interval={self.template_refresh_interval}, '
            f'target_address="{self.target_address}", '
            f'wan_mac_list=[{str_array(self.wan_mac_list)}]'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            load_native_props_from_list(self, props, _ipfix_prop_list)

            wan_mac_list = props['wan_mac_list'] if 'wan_mac_list' in props.keys() else None
            if isinstance(wan_mac_list, list):
                self.wan_mac_list = []
                for v in wan_mac_list:
                    self.wan_mac_list.append(WanMacItem(v))

    def store(self):
        props = {k: getattr(self, k) for k in _ipfix_prop_list}
        return props


_liveflow_preferences_prop_list = [
    'config_check_interval',
    'debug_logging',
    'decryption_enabled',
    'enforce_tcp_3way_handshake',
    'flow_time_ipfix',
    'hashtable_size',
    'hostname_analysis',
    'https_port',
    'latency_enabled',
    'quality_enabled',
    'retransmissions_enabled',
    'rtp_enabled',
    'rtp_packets_disabled',
    'signaling_packet_window',
    'tcp_handshake_timeout',
    'tcp_orphan_timeout',
    'tcp_packets_disabled',
    'tcp_post_close_timeout',
    'tcp_wait_timeout',
    'tls_analysis',
    'tls_packet_window',
    'udp_packets_disabled',
    'udp_wait_timeout',
    'vlan_enabled',
    'voip_quality_percent',
    'web_enabled'
]


class LiveFlowPreferences(object):
    """The LiveFlowPreferences class has the attributes of LiveFlow preferences."""

    config_check_interval = 1000
    """The time interval (in milliseconds) at which LiveFlow should check for updates in the
    configuration file.
    """

    debug_logging = 0
    """Indicates how much debug logging to display in the log files:
    0 = None, 1 = Low, 2 = Medium, 3 = High, 4 = Verbose.
    """

    decryption_enabled = False
    """Whether LiveFlow performs decryption for HTTPS packets."""

    enforce_tcp_3way_handshake = False
    """Whether LiveFlow requires a 3-way handshake (SYN, SYN-ACK, ACK) for a TCP flow in order for
    it to be included in processing and analyzing.
    """

    flow_time_ipfix = True
    """Whether IPFIX flow time is relative to IPFIX intervals (True) or flow packets (False)."""

    hashtable_size = 0
    """Indicates the total number of active flows expected at any one time per stream
    (a value of 0 indicates that LiveFlow will auto-determine the correct value).
    """

    hostname_analysis = True
    """Whether LiveFlow performs hostname analysis."""

    https_port = 443
    """The HTTPS port."""

    ipfix = None
    """IPFIX preferences."""

    latency_enabled = True
    """Whether LiveFlow performs latency analysis."""

    quality_enabled = True
    """Whether LiveFlow performs TCP quality analysis."""

    retransmissions_enabled = True
    """Whether LiveFlow performs TCP retransmission analysis."""

    rtp_enabled = True
    """Whether LiveFlow performs RTP analysis."""

    rtp_packets_disabled = False
    """Whether LiveFlow ignores RTP packets."""

    signaling_packet_window = 0
    """Indicates how many packets per SIP flow should be run through the SIP analysis; LiveFlow
    will analyze the first number of indicated packets and then ignore the rest that follow
    (0 = unlimited).
    """

    tcp_handshake_timeout = 2000
    """Indicates the maximum amount of time (in milliseconds) to allow between packets in a TCP
    flow while waiting for a 3-Way handshake to complete before considering the current flow
    complete and starting a new flow (ignored if enforce_tcp_3way_handshake key is false).
    """

    tcp_orphan_timeout = 60000
    """Indicates the maximum amount of time (in milliseconds) to allow between packets in a TCP
    flow after receiving a 3-Way handshake (if the enforce_tcp_3way_handshake key is true) and
    before the flow has begun to close (before a FIN is seen) before considering the current
    flow complete and starting a new flow.
    """

    tcp_packets_disabled = False
    """Whether LiveFlow ignores TCP packets."""

    tcp_post_close_timeout = 1000
    """Indicates the maximum amount of time (in milliseconds) to keep a flow in the hash table
    after it has been completed.
    """

    tcp_wait_timeout = 3000
    """Indicates the maximum amount of time (in milliseconds) to allow between packets in a TCP
    flow while waiting for the flow to close (after the first FIN is seen) before considering
    the current flow complete and starting a new flow.
    """

    tls_analysis = True
    """Whether LiveFlow performs TLS analysis."""

    tls_packet_window = 16
    """Indicates how many packets per HTTPS flow should be looked at for TLS information."""

    udp_packets_disabled = False
    """Whether LiveFlow ignores UDP packets."""

    udp_wait_timeout = 3000
    """Indicates the maximum amount of time (in milliseconds) to allow between packets in a UDP
    flow before considering the current flow complete and starting a new flow.
    """

    vlan_enabled = True
    """Whether LiveFlow performs VLAN/VXLAN/MPLS analysis."""

    voip_quality_percent = 25
    """Represents a percentage indicating how strongly to weight the average VoIP quality score vs
    the worst VoIP quality score when computing the MOS score (0 means the score is based
    completely on the worst score, and 100 means that the score is based completely on the
    average).
    """

    web_enabled = False
    """Whether LiveFlow performs web analysis."""

    def __init__(self, props):
        self.config_check_interval = LiveFlowPreferences.config_check_interval
        self.debug_logging = LiveFlowPreferences.debug_logging
        self.decryption_enabled = LiveFlowPreferences.decryption_enabled
        self.enforce_tcp_3way_handshake = LiveFlowPreferences.enforce_tcp_3way_handshake
        self.flow_time_ipfix = LiveFlowPreferences.flow_time_ipfix
        self.hashtable_size = LiveFlowPreferences.hashtable_size
        self.hostname_analysis = LiveFlowPreferences.hostname_analysis
        self.https_port = LiveFlowPreferences.https_port
        self.latency_enabled = LiveFlowPreferences.latency_enabled
        self.quality_enabled = LiveFlowPreferences.quality_enabled
        self.retransmissions_enabled = LiveFlowPreferences.retransmissions_enabled
        self.rtp_enabled = LiveFlowPreferences.rtp_enabled
        self.rtp_packets_disabled = LiveFlowPreferences.rtp_packets_disabled
        self.signaling_packet_window = LiveFlowPreferences.signaling_packet_window
        self.tcp_handshake_timeout = LiveFlowPreferences.tcp_handshake_timeout
        self.tcp_orphan_timeout = LiveFlowPreferences.tcp_orphan_timeout
        self.tcp_packets_disabled = LiveFlowPreferences.tcp_packets_disabled
        self.tcp_post_close_timeout = LiveFlowPreferences.tcp_post_close_timeout
        self.tcp_wait_timeout = LiveFlowPreferences.tcp_wait_timeout
        self.tls_analysis = LiveFlowPreferences.tls_analysis
        self.tls_packet_window = LiveFlowPreferences.tls_packet_window
        self.udp_packets_disabled = LiveFlowPreferences.udp_packets_disabled
        self.udp_wait_timeout = LiveFlowPreferences.udp_wait_timeout
        self.vlan_enabled = LiveFlowPreferences.vlan_enabled
        self.voip_quality_percent = LiveFlowPreferences.voip_quality_percent
        self.web_enabled = LiveFlowPreferences.web_enabled
        self._load(props)

    def __repr__(self):
        return (
            f'LiveFlowPreferences({{'
            f'config_check_interval: {self.config_check_interval}, '
            f'debug_logging: {self.debug_logging}, '
            f'decryption_enabled: {self.decryption_enabled}, '
            f'enforce_tcp_3way_handshake: {self.enforce_tcp_3way_handshake}, '
            f'flow_time_ipfix: {self.flow_time_ipfix}, '
            f'hashtable_size: {self.hashtable_size}, '
            f'hostname_analysis: {self.hostname_analysis}, '
            f'https_port: {self.https_port}, '
            f'ipfix: {{{repr(self.ipfix)}}}, '
            f'latency_enabled: {self.latency_enabled}, '
            f'quality_enabled: {self.quality_enabled}, '
            f'retransmissions_enabled: {self.retransmissions_enabled}, '
            f'rtp_enabled: {self.rtp_enabled}, '
            f'rtp_packets_disabled: {self.rtp_packets_disabled}, '
            f'signaling_packet_window: {self.signaling_packet_window}, '
            f'tcp_handshake_timeout: {self.tcp_handshake_timeout}, '
            f'tcp_orphan_timeout: {self.tcp_orphan_timeout}, '
            f'tcp_packets_disabled: {self.tcp_packets_disabled}, '
            f'tcp_post_close_timeout: {self.tcp_post_close_timeout}, '
            f'tcp_wait_timeout: {self.tcp_wait_timeout}, '
            f'tls_analysis: {self.tls_analysis}, '
            f'tls_packet_window: {self.tls_packet_window}, '
            f'udp_packets_disabled: {self.udp_packets_disabled}, '
            f'udp_wait_timeout: {self.udp_wait_timeout}, '
            f'vlan_enabled: {self.vlan_enabled}, '
            f'voip_quality_percent: {self.voip_quality_percent}, '
            f'web_enabled: {self.web_enabled}'
            f'}})'
        )

    def __str__(self):
        return (
            f'LiveFlowPreferences: '
            f'config_check_interval={self.config_check_interval}, '
            f'debug_logging={self.debug_logging}, '
            f'decryption_enabled={self.decryption_enabled}, '
            f'enforce_tcp_3way_handshake={self.enforce_tcp_3way_handshake}, '
            f'flow_time_ipfix={self.flow_time_ipfix}, '
            f'hashtable_size={self.hashtable_size}, '
            f'hostname_analysis={self.hostname_analysis}, '
            f'https_port={self.https_port}, '
            f'ipfix={{{str(self.ipfix)}}}, '
            f'latency_enabled={self.latency_enabled}, '
            f'quality_enabled={self.quality_enabled}, '
            f'retransmissions_enabled={self.retransmissions_enabled}, '
            f'rtp_enabled={self.rtp_enabled}, '
            f'rtp_packets_disabled={self.rtp_packets_disabled}, '
            f'signaling_packet_window={self.signaling_packet_window}, '
            f'tcp_handshake_timeout={self.tcp_handshake_timeout}, '
            f'tcp_orphan_timeout={self.tcp_orphan_timeout}, '
            f'tcp_packets_disabled={self.tcp_packets_disabled}, '
            f'tcp_post_close_timeout={self.tcp_post_close_timeout}, '
            f'tcp_wait_timeout={self.tcp_wait_timeout}, '
            f'tls_analysis={self.tls_analysis}, '
            f'tls_packet_window={self.tls_packet_window}, '
            f'udp_packets_disabled={self.udp_packets_disabled}, '
            f'udp_wait_timeout={self.udp_wait_timeout}, '
            f'vlan_enabled={self.vlan_enabled}, '
            f'voip_quality_percent={self.voip_quality_percent}, '
            f'web_enabled={self.web_enabled}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            load_native_props_from_list(self, props, _liveflow_preferences_prop_list)

            ipfix = props['ipfix'] if 'ipfix' in props.keys() else None
            if isinstance(ipfix, dict):
                self.ipfix = Ipfix(ipfix)

    def store(self):
        props = {k: getattr(self, k) for k in _liveflow_preferences_prop_list}
        if self.ipfix:
            props['ipfix'] = self.ipfix.store()
        return props


_liveflow_configuration_prop_list = [
    'version'
]


class LiveFlowConfiguration(object):
    """The LiveFlowConfiguration class has the attributes of LiveFlow configuration."""

    preferences = None
    """LiveFlow preferences."""

    services = []
    """List of LiveFlow services."""

    version = 0
    """LiveFlow configuration version."""

    def __init__(self, props):
        self._json = props
        self._load(props)

    def __repr__(self):
        return (
            f'LiveFlowConfiguration({{'
            f'preferences: {{{repr(self.preferences)}}}, '
            f'services: [{repr_array(self.services)}], '
            f'version: {self.version}'
            f'}})'
        )

    def __str__(self):
        return (
            f'LiveFlowConfiguration: '
            f'preferences={{{str(self.preferences)}}}, '
            f'services=[{str_array(self.services)}], '
            f'version={self.version}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            load_native_props_from_list(self, props, _liveflow_configuration_prop_list)

            preferences = props['preferences'] if 'preferences' in props.keys() else None
            if isinstance(preferences, dict):
                self.preferences = LiveFlowPreferences(preferences)
            else:
                preferences = props['perferences'] if 'perferences' in props.keys() else None
                if isinstance(preferences, dict):
                    self.preferences = LiveFlowPreferences(preferences)

            services = props['services'] if 'services' in props.keys() else None
            if isinstance(services, list):
                self.services = {v['nid']: v['sni'] for v in services}

    def _store(self):
        props = {a: getattr(self, a) for a in _liveflow_configuration_prop_list}
        if isinstance(self.preferences, LiveFlowPreferences):
            props['perferences'] = self.preferences.store()
        if isinstance(self.services, dict):
            props['services'] = [{'nid': k, 'sni': v} for k, v in self.services.items()]
        return props


_liveflow_license_dict = {
    'activeFlowCountLimit': 'active_flow_count_limit',
    'liveFlowEnabled': 'liveflow_enabled'
}


class LiveFlowLicense(object):
    """The LiveFlowLicense class has the attributes of LiveFlow licenses."""

    active_flow_count_limit = 0
    """The number of active flows that can be tracked at one time for a LiveFlow capture
    (0 = unlimited).
    """

    liveflow_enabled = True
    """Whether the Capture Engine supports LiveFlow."""

    def __init__(self, props):
        self.active_flow_count_limit = LiveFlowLicense.active_flow_count_limit
        self.liveflow_enabled = LiveFlowLicense.liveflow_enabled
        self._load(props)

    def __repr__(self):
        return (
            f'LiveFlowLicense({{'
            f'active_flow_count_limit: {self.active_flow_count_limit}, '
            f'liveflow_enabled: {self.liveflow_enabled}'
            f'}})'
        )

    def __str__(self):
        return (
            f'LiveFlow License: '
            f'active_flow_count_limit={self.active_flow_count_limit}, '
            f'liveflow_enabled={self.liveflow_enabled}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _liveflow_license_dict)

    def store(self):
        props = {}
        props['activeFlowCountLimit'] = self.active_flow_count_limit
        props['liveFlowEnabled'] = self.liveflow_enabled


_liveflow_context_dict = {
    'hostnameAnalysis': 'host_name_analysis',
    'ipfixAVCOutput': 'ipfix_avc_output',
    'ipfixFNFOutput': 'ipfix_fnf_output',
    'ipfixMediaNetOutput': 'ipfix_media_net_output',
    'ipfixSignalingDNOutput': 'ipfix_signaling_dn_output',
    'latencyAnalysis': 'latency_analysis',
    'rtpAnalysis': 'rtp_analysis',
    'tcp3WayHandshakeEnforcement': 'tcp_3way_handshake_enforcement',
    'tcpQualityAnalysis': 'tcp_quality_analysis',
    'tcpRetransmissionsAnalysis': 'tcp_retransmissions_analysis',
    'tlsAnalysis': 'tls_analysis',
    'tlsDecryption': 'tls_decryption',
    'vlanVxlanMplsAnalysis': 'vlan_vxlan_mpls_analysis',
    'webAnalysis': 'web_analysis'
}


class LiveFlowContext(object):
    """The LiveFlowContext class has the attributes of a LiveFlow context."""

    host_name_analysis = True
    """Whether LiveFlow performs hostname analysis."""

    ipfix_avc_output = True
    """Whether LiveFlow generates IPFIX AVC records."""

    ipfix_fnf_output = True
    """Whether LiveFlow generates IPFIX FNF records."""

    ipfix_media_net_output = True
    """Whether LiveFlow generates IPFIX MediaNet records."""

    ipfix_signaling_dn_output = True
    """Whether LiveFlow generates IPFIX Signaling DN records."""

    latency_analysis = True
    """Whether LiveFlow performs latency analysis."""

    license = None
    """LiveFlow license."""

    rtp_analysis = True
    """Whether LiveFlow performs RTP analysis."""

    tcp_3way_handshake_enforcement = True
    """Whether LiveFlow requires TCP flows to have a 3-way handshake."""

    tcp_quality_analysis = True
    """Whether LiveFlow performs TCP quality analysis."""

    tcp_retransmissions_analysis = True
    """Whether LiveFlow performs TCP retransmissions analysis."""

    tls_analysis = True
    """Whether LiveFlow performs TLS analysis."""

    tls_decryption = True
    """Whether LiveFlow performs TLS (<= v1.2) Decryption."""

    vlan_vxlan_mpls_analysis = True
    """Whether LiveFlow performs VLAN/VXLAN/MPLS analysis."""

    web_analysis = True
    """Whether LiveFlow performs HTTP/1.N web analysis."""

    def __init__(self, props):
        self.host_name_analysis = LiveFlowContext.host_name_analysis
        self.ipfix_avc_output = LiveFlowContext.ipfix_avc_output
        self.ipfix_fnf_output = LiveFlowContext.ipfix_fnf_output
        self.ipfix_media_net_output = LiveFlowContext.ipfix_media_net_output
        self.ipfix_signaling_dn_output = LiveFlowContext.ipfix_signaling_dn_output
        self.latency_analysis = LiveFlowContext.latency_analysis
        self.rtp_analysis = LiveFlowContext.rtp_analysis
        self.tcp_3way_handshake_enforcement = LiveFlowContext.tcp_3way_handshake_enforcement
        self.tcp_quality_analysis = LiveFlowContext.tcp_quality_analysis
        self.tcp_retransmissions_analysis = LiveFlowContext.tcp_retransmissions_analysis
        self.tls_analysis = LiveFlowContext.tls_analysis
        self.tls_decryption = LiveFlowContext.tls_decryption
        self.vlan_vxlan_mpls_analysis = LiveFlowContext.vlan_vxlan_mpls_analysis
        self.web_analysis = LiveFlowContext.web_analysis
        self._load(props)

    def __repr__(self):
        return (
            f'LiveFlowContext({{'
            f'host_name_analysis: {self.host_name_analysis}, '
            f'ipfix_avc_output: {self.ipfix_avc_output}, '
            f'ipfix_fnf_output: {self.ipfix_fnf_output}, '
            f'ipfix_media_net_output: {self.ipfix_media_net_output}, '
            f'ipfix_signaling_dn_output: {self.ipfix_signaling_dn_output}, '
            f'latency_analysis: {self.latency_analysis}, '
            f'license: {{{repr(self.license)}}}, '
            f'rtp_analysis: {self.rtp_analysis}, '
            f'tcp_3way_handshake_enforcement: {self.tcp_3way_handshake_enforcement}, '
            f'tcp_3way_handshake_enforcement: {self.tcp_3way_handshake_enforcement}, '
            f'tcp_retransmissions_analysis: {self.tcp_retransmissions_analysis}, '
            f'tls_analysis: {self.tls_analysis}, '
            f'tls_decryption: {self.tls_decryption}, '
            f'vlan_vxlan_mpls_analysis: {self.vlan_vxlan_mpls_analysis}, '
            f'web_analysis: {self.web_analysis}'
            f'}})'
        )

    def __str__(self):
        return (
            f'LiveFlowContext: '
            f'host_name_analysis={self.host_name_analysis}, '
            f'ipfix_avc_output={self.ipfix_avc_output}, '
            f'ipfix_fnf_output={self.ipfix_fnf_output}, '
            f'ipfix_media_net_output={self.ipfix_media_net_output}, '
            f'ipfix_signaling_dn_output={self.ipfix_signaling_dn_output}, '
            f'latency_analysis={self.latency_analysis}, '
            f'license={{{str(self.license)}}}, '
            f'rtp_analysis={self.rtp_analysis}, '
            f'tcp_3way_handshake_enforcement={self.tcp_3way_handshake_enforcement}, '
            f'tcp_3way_handshake_enforcement={self.tcp_3way_handshake_enforcement}, '
            f'tcp_retransmissions_analysis={self.tcp_retransmissions_analysis}, '
            f'tls_analysis={self.tls_analysis}, '
            f'tls_decryption={self.tls_decryption}, '
            f'vlan_vxlan_mpls_analysis={self.vlan_vxlan_mpls_analysis}, '
            f'web_analysis={self.web_analysis}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _liveflow_context_dict)

        if isinstance(props, dict):
            license = props['license'] if 'license' in props.keys() else None
            if isinstance(license, dict):
                self.license = LiveFlowLicense(license)

    def store(self):
        """Store attributes in a dictionary."""
        props = {}
        for k, v in _liveflow_license_dict.items():
            props[k] = getattr(self, v)
        return props


_liveflow_status_hash_tables_dict = {
    'activeFlowCountLimit': 'active_flow_count_limit',
    'capacity': 'capacity',
    'collisions': 'collisions',
    'deletions': 'deletions',
    'droppedInsertions': 'dropped_insertions',
    'id': 'id',
    'insertions': 'insertions',
    'maxContiguousFilledBuckets': 'max_contiguous_filled_buckets',
    'rtpInsertions': 'rtp_insertions',
    'size': 'size'
}


class HashTable(object):
    """The HashTable class has the attributes of a LiveFlow hash table."""

    active_flow_count_limit = 0
    """The number of active flows that are currently being tracked by the hash table."""

    capacity = 0
    """The capacity of the hash table."""

    collisions = 0
    """The number of collisions for the hash table."""

    deletions = 0
    """The number of deletions for the hash table."""

    dropped_insertions = 0
    """The number of dropped insertions for the hash table."""

    id = 0
    """The id for the hash table."""

    insertions = 0
    """The number of insertions for the hash table."""

    max_contiguous_filled_buckets = 0
    """The number of max contiguous filled buckets for the hash table."""

    rtp_insertions = 0
    """The number of RTP insertions for the hash table."""

    size = 0
    """The size of the hash table."""

    def __init__(self, props):
        self._load(props)

    def __repr__(self):
        return (
            f'HashTable({{'
            f'active_flow_count_limit: {self.active_flow_count_limit}, '
            f'capacity: {self.capacity}, '
            f'collisions: {self.collisions}, '
            f'deletions: {self.deletions}, '
            f'dropped_insertions: {self.dropped_insertions}, '
            f'id: {self.id}, '
            f'insertions: {self.insertions}, '
            f'max_contiguous_filled_buckets: {self.max_contiguous_filled_buckets}, '
            f'rtp_insertions: {self.rtp_insertions}, '
            f'size: {self.size}'
            f'}})'
        )

    def __str__(self):
        return (
            f'LiveFlow Status Hash Tables: '
            f'active_flow_count_limit={self.active_flow_count_limit}, '
            f'capacity={self.capacity}, '
            f'collisions={self.collisions}, '
            f'deletions={self.deletions}, '
            f'dropped_insertions={self.dropped_insertions}, '
            f'id={self.id}, '
            f'insertions={self.insertions}, '
            f'max_contiguous_filled_buckets={self.max_contiguous_filled_buckets}, '
            f'rtp_insertions={self.rtp_insertions}, '
            f'size={self.size}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _liveflow_status_hash_tables_dict)

    def store(self):
        """Store attributes in a dictionary."""
        props = {}
        for k, v in _liveflow_status_hash_tables_dict.items():
            props[k] = getattr(self, v)
        return props


_record_stats_dict = {
    'ipfixAVCCount': 'ipfix_avc_count',
    'ipfixFNFCount': 'ipfix_fnf_count',
    'ipfixMediaNetCount': 'ipfix_media_net_count',
    'ipfixSignalingDNIPv4Count': 'ipfix_signaling_dn_ipv4_count',
    'ipfixSignalingDNIPv6Count': 'ipfix_signaling_dn_ipv6_count'
}


class RecordStatistics(object):
    """The RecordStatistics class has the attributes of LiveFlow records."""

    ipfix_avc_count = 0
    """The number of IPFIX AVC records sent."""

    ipfix_fnf_count = 0
    """The number of IPFIX FNF records sent."""

    ipfix_media_net_count = 0
    """The number of IPFIX MediaNet records sent."""

    ipfix_signaling_dn_ipv4_count = 0
    """The number of IPFIX Signaling DN IPv4 records sent."""

    ipfix_signaling_dn_ipv6_count = 0
    """The number of IPFIX Signaling DN IPv6 records sent."""

    def __init__(self, props):
        self.ipfix_avc_count = RecordStatistics.ipfix_avc_count
        self.ipfix_fnf_count = RecordStatistics.ipfix_fnf_count
        self.ipfix_media_net_count = RecordStatistics.ipfix_media_net_count
        self.ipfix_signaling_dn_ipv4_count = RecordStatistics.ipfix_signaling_dn_ipv4_count
        self.ipfix_signaling_dn_ipv6_count = RecordStatistics.ipfix_signaling_dn_ipv6_count
        self._load(props)

    def __repr__(self):
        return (
            f'RecordStatistics({{'
            f'ipfix_avc_count: {self.ipfix_avc_count}, '
            f'ipfix_fnf_count: {self.ipfix_fnf_count}, '
            f'ipfix_media_net_count: {self.ipfix_media_net_count}, '
            f'ipfix_signaling_dn_ipv4_count: {self.ipfix_signaling_dn_ipv4_count}, '
            f'ipfix_signaling_dn_ipv6_count: {self.ipfix_signaling_dn_ipv6_count}'
            f'}})'
        )

    def __str__(self):
        return (
            f'LiveFlow Status Records Sent: '
            f'ipfix_avc_count={self.ipfix_avc_count}, '
            f'ipfix_fnf_count={self.ipfix_fnf_count}, '
            f'ipfix_media_net_count={self.ipfix_media_net_count}, '
            f'ipfix_signaling_dn_ipv4_count={self.ipfix_signaling_dn_ipv4_count}, '
            f'ipfix_signaling_dn_ipv6_count={self.ipfix_signaling_dn_ipv6_count}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        load_props_from_dict(self, props, _record_stats_dict)

    def store(self):
        """Store attributes in a dictionary."""
        props = {}
        for k, v in _record_stats_dict.items():
            props[k] = getattr(self, v)
        return props


_liveflow_status_dict = {
    'activeFlowCount': 'active_flow_count',
    'captureStartTime': 'capture_start_time',
    'flowsRejected': 'flows_rejected',
    'flowsRTPZeroPacket': 'flows_rtp_zero_packet',
    'flowsSeen': 'flows_seen',
    'packetsAccepted': 'packets_accepted',
    'packetsRejected': 'packets_rejected',
    'packetsSeen': 'packets_seen'
}


class LiveFlowStatus(object):
    """The LiveFlowStatus class has the attributes of LiveFlow status."""

    active_flow_count = 0
    """The number of active flows that are currently being tracked by LiveFlow."""

    capture_start_time = ''
    """In ISO 8601 format: CCYY-MM-DDThh:mm:ss.sssssssssZ. Will be null if the
    capture has never been started.
    """

    flows_rejected = 0
    """The number of flows rejected by LiveFlow due to the active flow count limit."""

    flows_rtp_zero_packet = 0
    """The number of RTP zero packet flows detected by LiveFlow."""

    flows_seen = 0
    """The number of flows seen by LiveFlow."""

    hash_table = []
    """The LiveFlow hash table status"""

    records_sent = None
    """The array of records sent by LiveFlow."""

    packets_accepted = 0
    """The number of packets accepted and analyzed by LiveFlow."""

    packets_rejected = 0
    """The number of packets rejected by LiveFlow."""

    packets_seen = 0
    """The number of packets seen by LiveFlow."""

    def __init__(self, props):
        self.active_flow_count = LiveFlowStatus.active_flow_count
        self.capture_start_time = LiveFlowStatus.capture_start_time
        self.flows_rejected = LiveFlowStatus.flows_rejected
        self.flows_rtp_zero_packet = LiveFlowStatus.flows_rtp_zero_packet
        self.flows_seen = LiveFlowStatus.flows_seen
        self.packets_accepted = LiveFlowStatus.packets_accepted
        self.packets_rejected = LiveFlowStatus.packets_rejected
        self.packets_seen = LiveFlowStatus.packets_seen
        self._load(props)

    def __repr__(self):
        return (
            f'LiveFlowStatus({{'
            f'active_flow_count: {self.active_flow_count}, '
            f'capture_start_time: "{self.capture_start_time}", '
            f'flows_rejected: {self.flows_rejected}, '
            f'flows_rtp_zeroPacket: {self.flows_rtp_zero_packet}, '
            f'flows_seen: {self.flows_seen}, '
            f'hash_table: [{repr_array(self.hash_table)}], '
            f'records_sent: {{{repr(self.records_sent)}}}, '
            f'packets_accepted: {self.packets_accepted}, '
            f'packets_rejected: {self.packets_rejected}, '
            f'packets_seen: {self.packets_seen}'
            f'}})'
        )

    def __str__(self):
        return (
            f'LiveFlowStatus: '
            f'active_flow_count={self.active_flow_count}, '
            f'capture_start_time="{self.capture_start_time}", '
            f'flows_rejected={self.flows_rejected}, '
            f'flows_rtp_zeroPacket={self.flows_rtp_zero_packet}, '
            f'flows_seen={self.flows_seen}, '
            f'hash_table=[{repr_array(self.hash_table)}], '
            f'records_sent={{{repr(self.records_sent)}}}, '
            f'packets_accepted={self.packets_accepted}, '
            f'packets_rejected={self.packets_rejected}, '
            f'packets_seen={self.packets_seen}'
        )

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            load_props_from_dict(self, props, _liveflow_status_dict)

            hash_table = props['hashTable'] if 'hashTable' in props.keys() else None
            if isinstance(hash_table, list):
                self.hash_table = [HashTable(v) for v in hash_table]

            record_stats = props['recordsSent'] if 'recordsSent' in props.keys() else None
            if isinstance(record_stats, dict):
                self.records = RecordStatistics(record_stats)


class LiveFlow(object):
    """The LiveFlow class is an interface into LiveFlow operations."""

    engine = None
    """OmniEngine interface."""

    def __init__(self, engine):
        self.engine = engine

    def __repr__(self):
        return f'LiveFlow({repr(self.engine)})'

    def __str__(self):
        return 'LiveFlow'

    def get_liveflow_configuration(self) -> Union[LiveFlowConfiguration, None]:
        """Gets the LiveFlow configuration"""
        if self.engine is not None:
            command = 'liveflow/configuration/'
            pr = self.engine.perf('get_liveflow_configuration')
            resp = self.engine._issue_command(command, pr)
            if not isinstance(resp, dict):
                raise OmniError('Failed to get LiveFlow configuration.')
            return LiveFlowConfiguration(resp)
        return None

    def get_liveflow_context(self) -> Union[LiveFlowContext, None]:
        """Gets the LiveFlow context"""
        if self.engine is not None:
            command = 'liveflow/context/'
            pr = self.engine.perf('get_liveflow_context')
            resp = self.engine._issue_command(command, pr)
            if not isinstance(resp, dict):
                raise OmniError('Failed to get LiveFlow context.')
            return LiveFlowContext(resp)
        return None

    def get_liveflow_status(self) -> Union[LiveFlowStatus, None]:
        """Gets the LiveFlow status"""
        if self.engine is not None:
            command = 'liveflow/status/'
            pr = self.engine.perf('get_liveflow_status')
            resp = self.engine._issue_command(command, pr)
            if not isinstance(resp, dict):
                raise OmniError('Failed to get LiveFlow status.')
            return LiveFlowStatus(resp)
        return None

    def set_liveflow_configuration(self, config: LiveFlowConfiguration) -> bool:
        """Sets the LiveFlow configuration"""
        if self.engine is not None:
            command = 'liveflow/configuration/'
            pr = self.engine.perf('set_liveflow_configuration')
            resp = self.engine._issue_command(
                command, pr, EO.POST, data=json.dumps(config._store(), cls=OmniScriptEncoder))
            if not isinstance(resp, dict):
                raise OmniError('Failed to set LiveFlow context.')
            reboot = resp['rebootRequired'] if 'rebootRequired' in resp else False
            return reboot
        return None
