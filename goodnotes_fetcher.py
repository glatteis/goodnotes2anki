from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import base64
from os import makedirs
import config
from fake_useragent import UserAgent


is_canvas_blank = """
// returns true if every pixel's uint32 representation is 0 (or "blank")
function isCanvasBlank(canvas) {
    const context = canvas.getContext('2d');
    const pixelBuffer = new Uint32Array(
        context.getImageData(0, 0, canvas.width, canvas.height).data.buffer
    );
    return !pixelBuffer.some(color => color !== 0);
}
"""
some_canvas_populated_script = is_canvas_blank + """
let elements = document.getElementsByTagName("canvas");
let list_of_elements = [];
if (elements.length == 0) {
    return false;
}
for (i = 0; i < elements.length; i++) {
    if (isCanvasBlank(elements[i])) {
        return false;
    }
    list_of_elements.push(elements[i].id);
}
return list_of_elements;
"""

def get_goodnotes_flashcards(goodnotes_url: str):
    if not goodnotes_url.startswith("https://share.goodnotes.com/s/"):
        raise ValueError("Invalid URL!")
    deck_id = goodnotes_url.replace("https://share.goodnotes.com/s/", "")
    folder = ".images/" + deck_id
    makedirs(folder, exist_ok=True)

    options = webdriver.ChromeOptions()
    # this needs to happen because GoodNotes "taints" their canvases
    options.add_argument("--disable-web-security")

    ua = UserAgent()
    user_agent = ua.random
    options.add_argument(f'user-agent={user_agent}')

    options.binary_location = config.chrome_location

    driver = webdriver.Chrome(config.chromedriver_location, chrome_options=options)
    driver.get(goodnotes_url)
    wait = WebDriverWait(driver, 1000, 0.2)
    
    # wait until some canvas is populated
    element = wait.until(
        lambda driver: driver.execute_script(some_canvas_populated_script)
    )

    thumbnails = driver.find_elements(By.CLASS_NAME, "thumbnail-container")
    
    output_images = []
    
    for i in reversed(list(range(len(thumbnails)))):
        thumbnail = thumbnails[i]
        thumbnail.click()
        wait.until(
            EC.visibility_of_all_elements_located((By.TAG_NAME, "canvas"))
        )
        # driver.execute_script("document.documentElement.style.setProperty(\"--scale\", \".01\");")
        canvasses = driver.find_elements(By.TAG_NAME, "canvas")
        # found_canvas_ids += [canvas.id for canvas in canvasses]
        elements = wait.until(
            lambda driver: driver.execute_script(some_canvas_populated_script)
        )
        image_parts = []
        for element in elements:
            canvas_base64 = driver.execute_script("return document.getElementById(arguments[0]).toDataURL('image/png');", element)
            canvas_png = base64.b64decode(canvas_base64[22:])
            filename = folder + "/" + element + ".png"
            with open(filename, 'wb') as f:
                f.write(canvas_png)
            image_parts.append(filename)
        output_images.append(image_parts)
    output_images.reverse()
    title = driver.title
    driver.close()
    return output_images, folder, title