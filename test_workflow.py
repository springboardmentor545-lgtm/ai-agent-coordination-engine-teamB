from workflow import app


result = app.invoke({
    "user_query": "Convert 100 USD to INR"
})

print("\n========== FINAL WORKFLOW RESULT ==========")

print("\nPLAN:")
print(result["plan"])

print("\nRESEARCH:")
print(result["research_result"])

print("\nANALYSIS:")
print(result["analysis"])

print("\nFINAL DECISION:")
print(result["final_decision"])