from agents import Agent, Runner, AgentOutputSchema
from pydantic import BaseModel
from typing import Literal

class History(BaseModel):
  title: str
  descriptors: list[str]
  hypothesis: str
  results: dict  # e.g. {"ctr": "-27%", "avd": "+14%", "outcome": "Retention improved, discovery worse"}

class EvaluationResult(BaseModel):
  evaluation: str
  hypothesis_result: str

async def run_evaluation_agent(period, stats, baseline, descriptors: list[str], video_script: str, history: list[History]):

    print("Running evaluation agent...")

    baseline_metrics = {
      "views": baseline.get(f"views_{period}"),
      "likes": baseline.get(f"likes_{period}"),
      "comments": baseline.get(f"comments_{period}"),
      "average_view_duration": baseline.get(f"average_view_duration_{period}"),
      "average_percentage_viewed": baseline.get(f"average_percentage_viewed_{period}"),
      "subs_gained": baseline.get(f"subs_gained_{period}"),
    }

    current_metrics = {
      "views": stats.get(f"views_{period}"),
      "likes": stats.get(f"likes_{period}"),
      "comments": stats.get(f"comments_{period}"),
      "average_view_duration": stats.get(f"average_view_duration_{period}"),
      "average_percentage_viewed": stats.get(f"average_percentage_viewed_{period}"),
      "subs_gained": stats.get(f"subs_gained_{period}"),
    }

    print("Current Metrics:")
    for key, value in current_metrics.items():
      print(f"  {key}: {value}")

    formatted_descriptors = "\n".join(
      [f"      <descriptor>{value}</descriptor>" for value in descriptors]
    )

    formatted_history = ""
    for h in history:
      history_descriptors = "\n".join([f"<descriptor>{d}</descriptor>" for d in h.descriptors])
      history_results = "\n".join([f"<{k}>{v}</{k}>" for k, v in h.results.items()])
      formatted_history += f"""
      <video>
        <title>{h.title}</title>
        <descriptors>{history_descriptors}</descriptors>
        <hypothesis>{h.hypothesis}</hypothesis>
        <results>{history_results}</results>
      </video>
      """

    prompt = f"""
    <evaluation>
      <instructions>
        You are a creative performance analyst for short-form video content.

        Your goals:
        1. Compare the current video’s metrics against baseline and past video history.
        2. Identify patterns across history (e.g., script style, hook type, face presence) that correlate with better or worse outcomes.
        3. Evaluate whether the hypothesis tested in the current video led to a positive, neutral, or negative outcome.
        4. Provide actionable recommendations for the next iteration.
        5. Output a final determination on the success of the Hypothesis ("Success", "Failure", "Neutral")

        Always structure your response strictly inside the <report> XML schema.
      </instructions>

      <data>
        <baselines>
          <views>{baseline_metrics['views']}</views>
          <likes>{baseline_metrics['likes']}</likes>
          <comments>{baseline_metrics['comments']}</comments>
          <average_view_duration>{baseline_metrics['average_view_duration']}</average_view_duration>
          <average_percentage_viewed>{baseline_metrics['average_percentage_viewed']}</average_percentage_viewed>
          <subs_gained>{baseline_metrics['subs_gained']}</subs_gained>
        </baselines>
        <history>
          {formatted_history}
        </history>
      </data>

      <response>
        <report>
          <what_went_well></what_went_well>
          <what_didnt_go_well></what_didnt_go_well>
          <test_result></test_result>
          <comparative_patterns></comparative_patterns>
          <suggestions></suggestions>
        </report>
      </response>
    </evaluation>
    """

    agent = Agent(
      name="Content Analysis Agent",
      instructions=prompt,
      output_type=AgentOutputSchema(EvaluationResult, strict_json_schema=True),
    )

    input = f"""<current_video>
      <views>{current_metrics['views']}</views>
      <likes>{current_metrics['likes']}</likes>
      <comments>{current_metrics['comments']}</comments>
      <average_view_duration>{current_metrics['average_view_duration']}</average_view_duration>
      <average_percentage_viewed>{current_metrics['average_percentage_viewed']}</average_percentage_viewed>
      <subs_gained>{current_metrics['subs_gained']}</subs_gained>
    </current_video>
    <hypothesis>Face visible in first 3 seconds</hypothesis>
    <descriptors>
      {formatted_descriptors}
    </descriptors>"""

    result = await Runner.run(agent, input)

    print("Evaluation Report:")
    print(result)

    return result.final_output

async def run_report_agent(evaluation: str):
  
  report_agent = Agent(
    name="Report Writer Agent",
    instructions=f"""
      <background>
      You are a report writer that takes evaluation results and formats them into a structured report.
      </background>
      <task>
      The provided evaluation report uses an XML format to structure the key findings and recommendations. Your task is to generate a human readable report that captures the essence of the evaluation while maintaining clarity and coherence.
      </task>
      <output>
      A plain text, human-readable report summarizing the key findings and recommendations from the evaluation.
      </output>
    """,
    model="gpt-4o-mini",
  )

  result = await Runner.run(report_agent, evaluation)

  print("Report Result:")
  print(result)

  return result.final_output

class NotionBlock(BaseModel):
  type: Literal["paragraph", "heading1", "heading_2", "link_preview", "image", "numbered_list_item"]
  text: str

class NotionBlocks(BaseModel):
  blocks: list[NotionBlock]

async def run_text_to_json_agent(text: str) -> dict:

  text_to_json_writer = Agent(
    name="Text to JSON Content Formatter",
    instructions=f"""
      <background>
      You are a content formatter that takes text content and formats it into JSON blocks.
      </background>
      <task>
      Format the content provided to you into the defined output structure in the output type section. You are able to create blocks of type paragraph, heading_2, and link_preview. Each block should have a type and text field. If the block is a link_preview, it should also have a url field which is link to the source of the content. Remove any markdown formatting which is not necessary for the JSON structure.
      </task>
    """,
    output_type=AgentOutputSchema(NotionBlocks, strict_json_schema=True),
    model="gpt-4o-mini",
  )

  result = await Runner.run(text_to_json_writer, text)

  print("Text to JSON Result:")
  print(result)

  return result.final_output