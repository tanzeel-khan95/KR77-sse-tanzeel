#!/usr/bin/env python3
import os
import aws_cdk as cdk

from currency_exchange_tracker.currency_exchange_tracker_stack import CurrencyExchangeTrackerStack

app = cdk.App()
CurrencyExchangeTrackerStack(app, "CurrencyExchangeTrackerStack")

app.synth()
