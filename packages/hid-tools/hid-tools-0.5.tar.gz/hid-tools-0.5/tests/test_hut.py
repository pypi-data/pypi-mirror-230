#!/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from hidtools.hut import HUT

import logging
import pytest

logger = logging.getLogger("hidtools.test.hut")


class TestHUT(object):
    pages = {
        0x00: "Undefined",
        0x01: "Generic Desktop",
        0x02: "Simulation Controls",
        0x03: "VR Controls",
        0x04: "Sports Controls",
        0x05: "Gaming Controls",
        0x06: "Generic Device Controls",
        0x07: "Keyboard",
        0x08: "LEDs",
        0x09: "Button",
        0x0A: "Ordinals",
        0x0B: "Telephony Devices",
        0x0C: "Consumer Devices",
        0x0D: "Digitizers",
        0x0E: "Haptic",
        0x10: "Unicode",
        0x12: "Eye and Head Trackers",
        0x14: "Auxiliary Display",
        0x20: "Sensor",
        0x40: "Medical Instruments",
        0x41: "Braille Display",
        0x59: "Lighting and Illumination",
        0x80: "Monitor",
        0x81: "Monitor Enumerated Values",
        0x82: "VESA Virtual Controls",
        0x83: "VESA Command",
        0x84: "Power Device",
        0x85: "Battery System",
        0x8C: "Bar Code Scanner",
        0x8D: "Scale",
        0x8E: "Magnetic Stripe Reading",
        0x90: "Camera Control",
        0x91: "Arcade Page OAAF",
        0x92: "Gaming Device",
        0xF1D0: "FIDO Alliance",
        0xFF00: "Vendor Defined Page 1",
        0xFF0D: "Wacom",
    }

    def test_hut_exists(self):
        assert HUT is not None

    def test_hut_size(self):
        # Update this test when a new Usage Page is added
        assert len(HUT) == 37

    def test_usage_pages(self):
        pages = self.pages
        empty_pages = ["Unicode", "Battery System", "Gaming Device"]

        for page_id, name in pages.items():
            page = HUT[page_id]
            assert page.page_id == page_id
            assert page.page_name == name
            print(page, page.page_name)
            if page.page_name in empty_pages:
                assert dict(page.from_name.items()) == {}
                assert dict(page.from_usage.items()) == {}
            else:
                assert dict(page.from_name.items()) != {}
                assert dict(page.from_usage.items()) != {}

            assert HUT[page_id] == HUT[page_id << 16]

    def test_usage_page_names(self):
        assert sorted(self.pages.values()) == sorted(HUT.usage_page_names)
        assert HUT.usage_page_names["Generic Desktop"] == HUT.usage_pages[0x01]
        assert HUT["Generic Desktop"] == HUT.usage_pages[0x01]

    def test_usage_gd(self):
        usages = {
            0x00: "Undefined",
            0x01: "Pointer",
            0x02: "Mouse",
            0x03: "Reserved",
            0x04: "Joystick",
            0x05: "Game Pad",
            0x06: "Keyboard",
            0x07: "Keypad",
            0x08: "Multi Axis",
            0x09: "Reserved",
            0x0A: "Water Cooling Device",
            0x0B: "Computer Chassis Device",
            0x0C: "Wireless Radio Controls",
            0x0D: "Portable Device Control",
            0x0E: "System Multi-Axis Controller",
            0x0F: "Spatial Controller",
            0x10: "Assistive Control",
            0x30: "X",
            0x31: "Y",
            0x32: "Z",
            0x33: "Rx",
            0x34: "Ry",
            0x35: "Rz",
            0x36: "Slider",
            0x37: "Dial",
            0x38: "Wheel",
            0x39: "Hat switch",
            0x3A: "Counted Buffer",
            0x3B: "Byte Count",
            0x3C: "Motion",
            0x3D: "Start",
            0x3E: "Select",
            0x3F: "Reserved",
            0x40: "Vx",
            0x41: "Vy",
            0x42: "Vz",
            0x43: "Vbrx",
            0x44: "Vbry",
            0x45: "Vbrz",
            0x46: "Vno",
            0x47: "Feature",
            0x48: "Resolution Multiplier",
            0x49: "Qx",
            0x4A: "Qy",
            0x4B: "Qz",
            0x4C: "Qw",
            0x80: "System Control",
            0x81: "System Power Down",
            0x82: "System Sleep",
            0x83: "System Wake Up",
            0x84: "System Context Menu",
            0x85: "System Main Menu",
            0x86: "System App Menu",
            0x87: "System Help Menu",
            0x88: "System Menu Exit",
            0x89: "System Menu Select",
            0x8A: "System Menu Right",
            0x8B: "System Menu Left",
            0x8C: "System Menu Up",
            0x8D: "System Menu Down",
            0x8E: "System Cold Restart",
            0x8F: "System Warm Restart",
            0x90: "D-Pad Up",
            0x91: "D-Pad Down",
            0x92: "D-Pad Right",
            0x93: "D-Pad Left",
            0x94: "Index Trigger",
            0x95: "Palm Trigger",
            0x96: "Thumbstick",
            0x97: "System Function Shift",
            0x98: "System Function Shift Lock",
            0x99: "System Function Shift Lock Indicator",
            0x9A: "System Dismiss Notification",
            0xA0: "System Dock",
            0xA1: "System UnDock",
            0xA2: "System Setup",
            0xA3: "System Break",
            0xA4: "System Debugger Break",
            0xA5: "Application Break",
            0xA6: "Application Debugger Break",
            0xA7: "System Speaker Mute",
            0xA8: "System Hibernate",
            0xB0: "System Display Invert",
            0xB1: "System Display Internal",
            0xB2: "System Display External",
            0xB3: "System Display Both",
            0xB4: "System Display Dual",
            0xB5: "System Display Toggle Internal External",
            0xB6: "System Display Swap Primary Secondary",
            0xB7: "System Display LCDAuto Scale",
            0xC0: "Sensor Zone",
            0xC1: "RPM",
            0xC2: "Coolant Level",
            0xC3: "Coolant Critical Level",
            0xC4: "Coolant Pump",
            0xC5: "Chassis Enclosure",
            0xC6: "Wireless Radio Button",
            0xC7: "Wireless Radio LED",
            0xC8: "Wireless Radio Slider Switch",
            0xC9: "System Display Rotation Lock Button",
            0xCA: "System Display Rotation Lock Slider Switch",
            0xCB: "Control Enable",
        }

        page = HUT[0x1]
        for u, uname in usages.items():
            if uname == "Reserved":
                continue

            usage = page[u]
            assert usage.name == uname
            assert usage.usage == u
            assert page[u] == page.from_name[uname]
            assert page[u] == page.from_usage[u]

        for i in range(0xFFFF):
            if i not in usages or usages[i] == "Reserved":
                assert i not in page

    def test_32_bit_usage_lookup(self):
        assert HUT[0x1][0x1 << 16 | 0x31].name == "Y"
        assert HUT[0x1][0x1 << 16 | 0x30].name == "X"
        assert HUT[0x2][0x2 << 16 | 0x09].name == "Airplane Simulation Device"
        assert HUT[0x2][0x2 << 16 | 0xB2].name == "Anti-Torque Control"

        with pytest.raises(KeyError):
            HUT[0x01][0x2 << 16 | 0x1]

    def test_duplicate_pages(self):
        # make sure we have no duplicate pages
        for p in HUT:
            page = HUT[p]
            if page == {} or page == {0: "Undefined"}:
                continue

            keys = list(HUT)
            keys.remove(p)
            for k in keys:
                assert page != HUT[k]

    def test_up01_generic_desktop(self):
        assert HUT[0x01].page_name == "Generic Desktop"
        assert HUT[0x01][0x0A].name == "Water Cooling Device"
        assert HUT[0x01][0x10].name == "Assistive Control"
        assert HUT[0x01][0x9A].name == "System Dismiss Notification"

    def test_up12_eye_and_head_trackers(self):
        assert HUT[0x12].page_name == "Eye and Head Trackers"
        assert HUT[0x12][0x1].name == "Eye Tracker"
        assert HUT[0x12][0x205].name == "Calibrated Screen Height"
        assert HUT[0x12][0x400].name == "Device Mode Request"

    def test_up0c_consumer_devices(self):
        assert HUT[0x0C].page_name == "Consumer Devices"
        assert HUT[0x0C][0x29E].name == "AC Navigation Guidance"

        # HUTRR32: 1C8 AL Message Status
        # HUTRR75: 1C8 AL Navigation
        assert HUT[0x0C][0x1C8].name == "AL Message Status"

        # HUTRR32: 2A0  ACSoft Key Left
        # HUTRR77: 2A0  AC Desktop Show All Applications
        assert HUT[0x0C][0x2A0].name == "ACSoft Key Left"

    def test_up0d_digitizers(self):
        assert HUT[0x0D].page_name == "Digitizers"
        assert HUT[0x0D][0x24].name == "Character Gesture"
        assert HUT[0x0D][0x61].name == "Gesture Character Quality"
        assert HUT[0x0D][0x69].name == "UTF32 Big Endian Character Gesture Encoding"
        # HUTRR76: 6A Gesture Character Enable
        # HUTRR87: 6A Capacitive Heat Map Protocol Vendor ID
        assert HUT[0x0D][0x6A].name == "Gesture Character Enable"
        assert HUT[0x0D][0x6B].name == "Capacitive Heat Map Protocol Version"
        assert HUT[0x0D][0x98].name == "Microsoft Pen Protocol"

    def test_up20_sensor(self):
        assert HUT[0x20].page_name == "Sensor"
        assert HUT[0x20][0x3A].name == "Environmental: Object Presence"
        assert HUT[0x20][0x43A].name == "Data Field: Object Presence"

    def test_up41_braille_display(self):
        assert HUT[0x41].page_name == "Braille Display"
        assert HUT[0x41][0x03].name == "8 Dot Braille Cell"
        assert HUT[0x41][0x100].name == "Router Button"
        assert HUT[0x41][0x210].name == "Braille Joystick Center"

    def test_up59_lighting_and_illumination(self):
        assert HUT[0x59].page_name == "Lighting and Illumination"
        assert HUT[0x59][0x7].name == "Lamp Array Kind"
        assert HUT[0x59][0x22].name == "Lamp Attributes Response Report"
        assert HUT[0x59][0x53].name == "Blue Update Channel"

    def test_up84_power_device(self):
        assert HUT[0x84].page_name == "Power Device"
        assert HUT[0x84][0x06].name == "Peripheral Device"
