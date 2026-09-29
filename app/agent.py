# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from app.a2ui_utils import a2ui_callback
from app.tools import (
    save_search_criteria,
    discover_jobs,
    score_job_fit,
    tailor_resume,
    track_application,
    update_application_status,
    parse_inbound_emails,
    research_interview_and_referrals,
)

schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are JOB SEARCH AUTOPILOT, an advanced autonomous agent that handles the entire job search lifecycle. "
        "Your core capabilities are: "
        "1. PROMPT STUDIO: Save and parse natural language user criteria into structured filters. "
        "2. DISCOVERY ENGINE: Pull and deduplicate jobs across ATS boards and the web. "
        "3. RANKING & FIT SCORING: Score each job (0-100) against active criteria using LLM evaluation. "
        "4. RESUME TAILORING: Tailor master profiles for specific jobs without fabricating facts. "
        "5. TRACKER DASHBOARD: Track jobs, fit scores, resumes, and research. "
        "6. EMAIL INTELLIGENCE: Parse inbound emails to auto-advance application statuses.\n\n"
        "Always use your tools to provide these capabilities seamlessly."
    ),
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-3.1-pro",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    tools=[
        save_search_criteria,
        discover_jobs,
        score_job_fit,
        tailor_resume,
        track_application,
        update_application_status,
        parse_inbound_emails,
        research_interview_and_referrals,
    ],
    after_model_callback=a2ui_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
