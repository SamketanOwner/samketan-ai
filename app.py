                            + "</p>"
                            + esc_reason_html
                            + "</div></div>",
                            unsafe_allow_html=True,
                        )
                except Exception as e:
                    st.error("Auto-Responder Error: " + str(e))

        with pipeline_status_placeholder.container():
            show_agent_pipeline({"gemini": "done", "claude": "done", "gpt": "done", "auto": "done"})

        st.balloons()
        st.success("Full Multi-Agent Pipeline Complete! Your leads are researched, analysed, messaged and conversation-ready.")

        st.markdown("### Export Complete Intelligence Report")
        dl_col1, dl_col2 = st.columns(2)
        with dl_col1:
            leads_data = st.session_state.leads_data or []
            if leads_data:
                df_leads = pd.DataFrame(leads_data)
                st.download_button(
                    "Download Leads CSV",
                    data=df_leads.to_csv(index=False).encode("utf-8"),
                    file_name="samketan_leads_" + region.replace(",", "_").replace(" ", "_") + ".csv",
                    mime="text/csv",
                    use_container_width=True,
                )
        with dl_col2:
            full_report = {
                "generated_at": datetime.now().isoformat(),
                "inputs": {
                    "product": my_product,
                    "region": region,
                    "target_client": target_client,
                    "scope": scope,
                    "urgency": urgency,
                },
                "pipeline_results": st.session_state.pipeline_results,
            }
            st.download_button(
                "Download Full JSON Report",
                data=json.dumps(full_report, indent=2, default=str).encode("utf-8"),
                file_name="samketan_full_report_" + region.replace(",", "_").replace(" ", "_") + ".json",
                mime="application/json",
                use_container_width=True,
            )


# ---------------------------------------------
# MANUAL CLIENT REPLY SIMULATION
# ---------------------------------------------
if simulate_reply and st.session_state.pipeline_results:
    st.markdown("---")
    show_phase_header(
        "phase-auto",
        "&#128172;",
        "Manual Reply Simulation",
        "Enter a client reply and see AI auto-response",
    )

    client_reply_input = st.text_area(
        "Paste a client's actual reply here:",
        placeholder="e.g. Hello, we are interested. Can you share more details about pricing and location?",
        height=100,
    )
    reply_company = st.text_input("Which company replied?", placeholder="Company name...")

    if st.button("Generate Smart Auto-Reply") and client_reply_input:
        with st.spinner("Generating intelligent response..."):
            try:
                model, _ = get_gemini_model()
                manual_prompt = (
                    "You are the sales AI for "
                    + our_company
                    + ".\n\n"
                    "OUR OFFERING: "
                    + our_product
                    + "\n"
                    "TONE: "
                    + reply_tone
                    + "\n"
                    "COMPANY THAT REPLIED: "
                    + reply_company
                    + "\n\n"
                    "CLIENT REPLIED: "
                    + client_reply_input
                    + "\n\n"
                    "Write a professional, helpful response that:\n"
                    "1. Directly addresses their message\n"
                    "2. Provides relevant details from our offering\n"
                    "3. Moves toward scheduling a site visit or call\n"
                    "4. Is warm and not pushy\n\n"
                    "CRITICAL: Return ONLY a valid JSON object. No markdown. No backticks. No explanation.\n"
                    "The object MUST have these exact keys:\n"
                    "- whatsapp_reply (string)\n"
                    "- email_reply (string)\n"
                    "- next_step (string)\n\n"
                    "Start your response with { and end with }"
                )
                manual_res = call_gemini_with_retry(model, manual_prompt)
                manual_data = safe_json_parse(manual_res.text, {})

                if manual_data:
                    st.markdown(
                        '<div class="autoreply-box">'
                        '<div class="autoreply-label">WhatsApp Auto-Reply for '
                        + esc(reply_company)
                        + "</div>"
                        '<div class="autoreply-text">'
                        + esc(manual_data.get("whatsapp_reply", ""))
                        + "</div></div>"
                        '<div class="msg-box msg-email">'
                        '<div class="msg-label msg-label-mail">Email Auto-Reply</div>'
                        '<div class="msg-content">'
                        + esc(manual_data.get("email_reply", ""))
                        + "</div></div>"
                        '<div style="background:#0a0d14;border:1px solid #1e2a3e;border-radius:8px;padding:12px 16px;margin-top:10px;">'
                        '<p style="font-size:0.72rem;color:#4a5568;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">Recommended Next Step</p>'
                        '<p style="color:#b0bec5;font-size:0.84rem;">'
                        + esc(manual_data.get("next_step", ""))
                        + "</p></div>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.warning("Could not parse response. Raw output:")
                    st.text(manual_res.text)
            except Exception as e:
                st.error("Manual reply error: " + str(e))

elif simulate_reply and not st.session_state.pipeline_results:
    st.warning("Run the pipeline first before simulating replies.")


# ---------------------------------------------
# FOOTER
# ---------------------------------------------
st.markdown("---")
st.markdown(
    '<p style="color:#2a3a4e;font-size:0.8rem;text-align:center;">'
    "Samketan AI v7.0 | Multi-Agent Autonomous Pipeline | 100% Free - Powered by Gemini | &copy; 2026 Samketan"
    "</p>",
    unsafe_allow_html=True,
)
