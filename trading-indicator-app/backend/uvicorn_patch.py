"""
Patch for Uvicorn to work with newer NumPy versions which don't expose NaN directly
"""
import os
import sys

def patch_uvicorn():
    try:
        import uvicorn
        subprocess_path = os.path.join(os.path.dirname(uvicorn.__file__), "_subprocess.py")
        
        with open(subprocess_path, 'r') as f:
            content = f.read()
        
        # Try different variations of the import statement
        import_variations = [
            "from numpy import NaN as npNaN",
            "from numpy import NaN",
            "import numpy.NaN"
        ]
        
        replacement = "from numpy import nan as npNaN"
        patched = False
        
        for variation in import_variations:
            if variation in content:
                patched_content = content.replace(variation, replacement)
                
                with open(subprocess_path, 'w') as f:
                    f.write(patched_content)
                
                print(f"Patched uvicorn _subprocess.py at {subprocess_path}")
                print(f"Replaced '{variation}' with '{replacement}'")
                patched = True
                break
        
        if not patched:
            # Print the relevant part of the file to debug
            print("Could not find any of the expected import statements. Here's a snippet of the file:")
            
            # Find lines that mention numpy and NaN
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "numpy" in line and ("NaN" in line or "nan" in line):
                    start = max(0, i-2)
                    end = min(len(lines), i+3)
                    print("\nRelevant section (lines {}-{}):".format(start+1, end))
                    for j in range(start, end):
                        print("{}: {}".format(j+1, lines[j]))
        
        return patched
    
    except Exception as e:
        print(f"Error patching uvicorn: {str(e)}")
        return False

if __name__ == "__main__":
    patch_uvicorn() 