import os
import sys
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from basic_mission_data import BasicMissionData
from technical_data import TechnicalData
from launch_data import LaunchData
from cost_and_other_data import CostAndOtherData
import json

def main():
    load_dotenv()
    satellite_name = "Aditya-L1"
    
    print(f"Testing Satellite Data Extraction Agents")
    print(f"Satellite: {satellite_name}")
    print("=" * 50)
    
    try:
        # Initialize all agents
        print("Initializing agents...")
        basic_mission = BasicMissionData()
        technical_data = TechnicalData()
        launch_data = LaunchData()
        cost_data = CostAndOtherData()
        
        # Extract basic mission data
        print(f"Extracting basic mission data for {satellite_name}...")
        basic_result = basic_mission.call(satellite_name)
        
        # Extract technical data
        print(f"Extracting technical data for {satellite_name}...")
        technical_result = technical_data.call(satellite_name)
        
        # Extract launch data
        print(f"Extracting launch data for {satellite_name}...")
        launch_result = launch_data.call(satellite_name)
        
        # Extract cost and other data
        print(f"Extracting cost and other data for {satellite_name}...")
        cost_result = cost_data.call(satellite_name)
        
        # Display individual results
        print("\nBASIC MISSION DATA RESULTS:")
        print("=" * 50)
        if "error" in basic_result:
            print(f"Error: {basic_result['error']}")
            if "raw_output" in basic_result:
                print(f"\nRaw Output:")
                print(basic_result["raw_output"])
        else:
            print("Successfully extracted basic mission data:")
            print("\nExtracted Information:")
            for key, value in basic_result.items():
                print(f"  {key}: {value}")
        
        print("\nTECHNICAL DATA RESULTS:")
        print("=" * 50)
        if "error" in technical_result:
            print(f"Error: {technical_result['error']}")
            if "raw_output" in technical_result:
                print(f"\nRaw Output:")
                print(technical_result["raw_output"])
        else:
            print("Successfully extracted technical data:")
            print("\nExtracted Information:")
            for key, value in technical_result.items():
                print(f"  {key}: {value}")
        
        print("\nLAUNCH DATA RESULTS:")
        print("=" * 50)
        if "error" in launch_result:
            print(f"Error: {launch_result['error']}")
            if "raw_output" in launch_result:
                print(f"\nRaw Output:")
                print(launch_result["raw_output"])
        else:
            print("Successfully extracted launch data:")
            print("\nExtracted Information:")
            for key, value in launch_result.items():
                print(f"  {key}: {value}")
        
        print("\nCOST AND OTHER DATA RESULTS:")
        print("=" * 50)
        if "error" in cost_result:
            print(f"Error: {cost_result['error']}")
            if "raw_output" in cost_result:
                print(f"\nRaw Output:")
                print(cost_result["raw_output"])
        else:
            print("Successfully extracted cost and other data:")
            print("\nExtracted Information:")
            for key, value in cost_result.items():
                print(f"  {key}: {value}")
        
        # Combine results into single JSON
        print("\nCOMBINED RESULTS:")
        print("=" * 50)
        combined_data = {
            "satellite_name": satellite_name,
            "extraction_status": {
                "basic_mission_data": "success" if "error" not in basic_result else "error",
                "technical_data": "success" if "error" not in technical_result else "error",
                "launch_data": "success" if "error" not in launch_result else "error",
                "cost_and_other_data": "success" if "error" not in cost_result else "error"
            },
            "basic_mission_data": basic_result if "error" not in basic_result else {"error": basic_result["error"]},
            "technical_data": technical_result if "error" not in technical_result else {"error": technical_result["error"]},
            "launch_data": launch_result if "error" not in launch_result else {"error": launch_result["error"]},
            "cost_and_other_data": cost_result if "error" not in cost_result else {"error": cost_result["error"]}
        }
        print("\nCombined JSON Output:")
        print(json.dumps(combined_data, indent=2))
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 