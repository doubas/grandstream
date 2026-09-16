# Grandstream UCM6304A HTTPS API Action Catalog

This catalog documents the **124 official HTTPS API actions** supported by Grandstream UCM PBX systems (firmware 1.0.33.x).

All actions are invoked via `POST https://<ucm-ip>:<port>/api` with `Content-Type: application/json;charset=UTF-8` and body `{"request": {"action": "<action_name>", "cookie": "<session_cookie>", ...}}`.

---

## 1. System, Session & Authentication

| Action | Purpose | Request Parameters | Response Key Fields |
|---|---|---|---|
| `challenge` | Retrieve 16-character auth challenge | `user`, `version: "1.0"` | `challenge` |
| `login` | Authenticate using MD5(challenge + password) | `user`, `token` (MD5 hex) | `cookie` |
| `logout` | Terminate session cookie | `cookie` | `status: 0` |
| `ping` | Keepalive / session refresh | `cookie` | `status: 0` |
| `getSystemStatus` | High-level system uptime and status | `cookie` | `cpu_usage`, `mem_usage`, `network` |
| `getSystemGeneralStatus` | Hardware model, serial, firmware, part number | `cookie` | `part_number`, `mac`, `prog_version`, `system_time` |
| `applyChanges` | Reload asterisk / PBX configuration changes | `cookie` | `status: 0` |

---

## 2. Accounts, Extensions & Users

| Action | Purpose | Key Parameters |
|---|---|---|
| `listAccount` | List all extensions and their basic status | `item_num`, `page` |
| `getSIPAccount` | Retrieve detailed SIP credentials, secret, authid | `extension` |
| `updateSIPAccount` | Update extension settings (secret, display name) | `extension`, `fullname`, `secret` |
| `addSIPAccountAndUser` | Create a new extension and associated user profile | `extension`, `fullname`, `secret`, `user_name` |
| `listUser` | List web/portal users | `item_num`, `page` |
| `getUser` | Get detailed user information | `user_name` |
| `updateUser` | Modify user attributes, email, role | `user_name`, `email`, `role` |
| `deleteUser` | Remove a portal user | `user_name` |
| `listExtensionGroup` | List extension departments/groups | `item_num`, `page` |
| `listDepartment` | List organizational departments | `item_num`, `page` |

---

## 3. Call Operations & Telephony Control

| Action | Purpose | Key Parameters |
|---|---|---|
| `dialExtension` | Originate a call between two extensions | `extension`, `target_extension` |
| `dialOutbound` | Originate an outbound call via a trunk | `extension`, `outbound_number` |
| `dialOutboundTwo` | Advanced outbound dial with specific route | `extension`, `outbound_number`, `trunk_index` |
| `dialIVR` | Dial directly into an IVR menu | `extension`, `ivr_id` |
| `dialIVROutbound` | Dial outbound into external IVR | `extension`, `outbound_number` |
| `dialQueue` | Route an extension directly to a call queue | `extension`, `queue_id` |
| `dialRinggroup` | Dial an internal ring group | `extension`, `ringgroup_id` |
| `callTransfer` | Transfer an active call to another target | `channel`, `target` |
| `hold` / `unhold` | Place active channel on hold / resume | `channel` |
| `mute` / `unmute` | Mute audio on an active channel / unmute | `channel` |
| `Hangup` | Terminate an active channel | `channel` |
| `refuseCall` | Reject incoming call on channel | `channel` |
| `listBridgedChannels` | List active two-way connected calls | `item_num`, `page` |
| `listUnBridgedChannels` | List ringing / unbridged call legs | `item_num`, `page` |

---

## 4. Trunks (Analog, SIP, SLA, DOD)

| Action | Purpose | Key Parameters |
|---|---|---|
| `listAnalogTrunk` | List all FXO / PSTN analog trunks | `item_num`, `page` |
| `getAnalogTrunk` | Get configuration of an analog trunk | `trunk_index` |
| `addAnalogTrunk` | Configure a new analog FXO trunk | `trunk_name`, `ports` |
| `updateAnalogTrunk` | Modify FXO trunk parameters | `trunk_index`, `trunk_name` |
| `deleteAnalogTrunk` | Remove an analog trunk | `trunk_index` |
| `listVoIPTrunk` | List all SIP / VoIP trunks | `item_num`, `page` |
| `getSIPTrunk` | Get details of a SIP trunk | `trunk_index` |
| `addSIPTrunk` | Create a new SIP peering/registration trunk | `trunk_name`, `host_name`, `user_name`, `secret` |
| `updateSIPTrunk` | Update SIP trunk parameters | `trunk_index`, ... |
| `deleteSIPTrunk` | Delete a SIP trunk | `trunk_index` |
| `listTrunkGroup` | List trunk load-balancing groups | `item_num`, `page` |
| `getOneTrunkGroupInfo` | Get trunk group details | `group_id` |
| `addSIPTrunkGroup` | Create a trunk group | `group_name`, `members` |
| `updateTrunkGroup` | Modify trunk group members | `group_id`, `members` |
| `deleteSIPTrunkGroup` | Remove a trunk group | `group_id` |
| `listDODVoIPTrunk` | List Direct Outward Dialing rules | `item_num`, `page` |
| `addDODVoIPTrunk` | Add DOD mapping | `trunk_index`, `number`, `extension` |
| `updateDODVoIPTrunk` | Update DOD mapping | `dod_index`, ... |
| `deleteDODVoIPTrunk` | Remove DOD mapping | `dod_index` |
| `addSLATrunk` / `updateSLATrunk` / `deleteSLATrunk` | Shared Line Appearance (SLA) trunks | `trunk_name`, `ports` |

---

## 5. Inbound & Outbound Routes & Blacklists

| Action | Purpose | Key Parameters |
|---|---|---|
| `listInboundRoute` | List all inbound call routing rules | `item_num`, `page` |
| `getInboundRoute` | Get specific inbound route configuration | `inbound_route_id` |
| `addInboundRoute` | Create an inbound routing rule | `pattern`, `trunk_index`, `destination_type`, `destination_id` |
| `updateInboundRoute` | Modify inbound routing rule | `inbound_route_id`, ... |
| `deleteInboundRoute` | Delete inbound route | `inbound_route_id` |
| `listOutboundRoute` | List outbound dialing rules | `item_num`, `page` |
| `getOutboundRoute` | Get specific outbound route configuration | `outbound_route_id` |
| `addOutboundRoute` | Create an outbound dialing route | `pattern`, `trunk_index`, `strip`, `prepend` |
| `updateOutboundRoute` | Modify outbound dialing route | `outbound_route_id`, ... |
| `deleteOutboundRoute` | Delete outbound route | `outbound_route_id` |
| `transferNumberInbound` | Reorder inbound routing priorities | `from_index`, `to_index` |
| `transferNumberOutbound` | Reorder outbound routing priorities | `from_index`, `to_index` |
| `listInboundBlacklist` | List blocked incoming caller numbers | `item_num`, `page` |
| `getInboundBlacklistSettings` | Query blacklist behavior settings | - |
| `addInboundBlacklist` | Add number to blacklist | `block_number` |
| `updateInboundBlacklist` | Edit blacklisted entry | `blacklist_id`, `block_number` |
| `updateInboundBlacklistSettings` | Enable/disable blacklist | `enable_blacklist` |
| `deleteInboundBlacklist` | Remove number from blacklist | `blacklist_id` |
| `deleteAllInboundBlacklist` | Flush entire blacklist | - |

---

## 6. Queues, IVR, Paging & Conferencing

| Action | Purpose | Key Parameters |
|---|---|---|
| `listQueue` | List all call queues | `item_num`, `page` |
| `getQueue` | Get details and agent list for a queue | `queue_id` |
| `getQueueCalling` | Real-time queue wait status & callers | `queue_id` |
| `addQueue` | Create a new call queue | `queue_name`, `strategy`, `members` |
| `updateQueue` | Modify queue settings | `queue_id`, ... |
| `deleteQueue` | Delete a call queue | `queue_id` |
| `loginLogoffQueueAgent` | Dynamically log agent in or out of queue | `queue_id`, `extension`, `action: "login"|"logoff"` |
| `pauseUnpauseQueueAgent` | Pause or unpause an agent in queue | `queue_id`, `extension`, `action: "pause"|"unpause"` |
| `queueapi` | Query agent real-time stats | `queue_id` |
| `listIVR` | List Interactive Voice Response menus | `item_num`, `page` |
| `getIVR` | Get IVR prompts and key press actions | `ivr_id` |
| `addIVR` | Create an IVR auto-attendant | `ivr_name`, `prompt`, `key_options` |
| `updateIVR` | Modify IVR menu options | `ivr_id`, ... |
| `deleteIVR` | Delete an IVR menu | `ivr_id` |
| `listPaginggroup` | List one-way / two-way paging groups | `item_num`, `page` |
| `getPaginggroup` | Get members of a paging group | `paginggroup_id` |
| `addPaginggroup` | Create paging group | `paginggroup_name`, `members` |
| `updatePaginggroup` | Update paging group | `paginggroup_id`, ... |
| `deletePaginggroup` | Delete paging group | `paginggroup_id` |
| `MulticastPaging` | Trigger a multicast audio broadcast | `paging_ip`, `paging_port`, `prompt` |
| `MulticastPagingHangup` | End multicast paging stream | `paging_id` |
| `addMeetNowForGeneral` | Start an ad-hoc conference bridge | `room_id`, `members` |
| `addMultimediaConferenceReservation` | Schedule a future video/audio conference | `room_id`, `start_time`, `end_time` |
| `getMultimediaConferenceReservation` | Get conference reservation details | `reservation_id` |
| `listMultimediaConferenceReservationInfo` | List scheduled conference bookings | `item_num`, `page` |
| `updateMultimediaConferenceReservation` | Edit scheduled conference | `reservation_id`, ... |
| `deleteMultimediaConferenceReservation` | Cancel scheduled conference | `reservation_id` |
| `HangupRoom` | Terminate all calls in conference room | `room_id` |
| `InviteUser` | Dial and pull user into active conference | `room_id`, `extension` |
| `KickUser` | Drop a participant from conference | `room_id`, `extension` |
| `UserMuteAudio` / `UserUnmuteAudio` | Mute/unmute conference participant | `room_id`, `extension` |
| `ConfSetLayout` / `ConfCancelLayout` | Video conference layout grid control | `room_id`, `layout_mode` |

---

## 7. CDR, Recordings, Contacts & PIN Sets

| Action | Purpose | Key Parameters |
|---|---|---|
| `cdrapi` | Query Call Detail Records (CDR) | `start_time`, `end_time`, `src`, `dst`, `page` |
| `recapi` | Query call audio recording files | `cdr_id`, `action` |
| `getRecordInfosByCall` | Retrieve recording metadata for specific call | `call_id` |
| `playPromptByOrg` | Stream/play voice prompt audio file | `prompt_name` |
| `cleanTerminalChatInformation`| Clear GS Wave terminal chat records | `user_name` |
| `listPinSets` | List PIN codes for restricted dialing | `item_num`, `page` |
| `getPinSets` | Get PIN code details | `pinsets_id` |
| `addPinSets` | Add a PIN authorization set | `pinset_name`, `pins` |
| `updatePinSets` | Modify PIN codes | `pinsets_id`, `pins` |
| `deletePinSets` | Delete PIN set | `pinsets_id` |
| `listContact` / `addContact` / `updateContact` / `deleteContact` | Manage centralized PBX phonebook | `name`, `number`, `email` |
| `listIPC` | List connected IP cameras / surveillance video endpoints | `item_num`, `page` |
| `pmsapi` | Property Management System integration query | `action_name` |
