
import requests
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
import time
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
import logging
import pymongo
import warnings 



class inureon_webscrapping():
    
    
    def __init__(self,driver_path,page_load_time):
        self.driver_path=driver_path
        self.page_load_time=page_load_time
        warnings.filterwarnings(action= 'ignore')
        logging.basicConfig(filename="current.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
       
        #Creating an object
        self.logger = logging.getLogger()

        # Setting the threshold of logger to DEBUG
        # logger.setLevel(logging.INFO)
        self.logger.info("Runing again")
        
        
    def course_categories(self):
        '''This Method  help us to get the categories and 
         there sub-categories's name and id attribute
         '''
        try:
            self.options = webdriver.ChromeOptions() 
            self.options.add_argument("start-maximized")
            self.options.add_argument("--auto-open-devtools-for-tabs")
            self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
            self.options.add_experimental_option('useAutomationExtension', False)
            self.driver = webdriver.Chrome(options=self.options, executable_path=self.driver_path)
            self.driver.get('https://ineuron.ai/')
            time.sleep(page_load_time)
            self.driver.find_element_by_xpath("//i[@onclick='if (!window.__cfRLUnblockHandlers) return false; closeModal()']").click()

            #click on menu icon
            self.driver.find_element_by_xpath("//img[@src='./images/hamburger.svg']").click()


            #click on courses
            self.driver.find_element_by_xpath("//li[@onclick='showMobileCategories()']").click()
            
            
            #To get all the courses name and id attribute
            
            category_set=self.driver.find_element_by_xpath("(//div[@class='sidebar-content'])[2]/ul")
            courses_categories= category_set.find_elements_by_tag_name("li")
            
            #passing catigories and subcategories "id" to "courses_url" method to get the subcatogries url
            all_course_dict=self.courses_url(courses_categories)
            
            
            #passing "all_course_dict" to "pass_categories_url" method to fetch the all courses details
            final_courses_detail=self.pass_categories_url(all_course_dict)
            return final_courses_detail
        
        except Exception as e:

            self.logger.info(f"Error thrown at course_categories method ,error is :-{e}")
            print(e)
        
        
        
        
    def courses_url(self,courses_categories):
        '''This method help to get categories ,sub-categories and sub-categories courses url  using
        id tag form course_categories method
        '''
        
        all_course_dict={}
        print("fetching url in Dictionary")
        for i in courses_categories:
            
            try:
                self.driver.find_element_by_id(i.get_attribute("id")).click()#click on courses name
                self.course=self.driver.find_element_by_xpath("(//div[@class='sidebar-content'])[3]/ul")#list of sub-course in courses

                self.course=wait(self.course,10).until(ec.presence_of_all_elements_located((By.TAG_NAME,'a')))#getting all the 'a' tag

                all_course_dict[i.text]=[j.get_attribute('href') for j in self.course]#storing the url for sub-courses

                
                self.elem=self.driver.find_element_by_xpath("//div[@onclick='closeMobileCategories()']/i")
                self.driver.execute_script("arguments[0].click();", self.elem)
                time.sleep(2)
            except Exception as e:
                    print("course " ,i.text," has thrown a exception of ",e)
                    self.logger.info(f"\"courses_url\" :- course {i.text}  has thrown a exception of {e}")
        self.driver.close()
        print("completed fetching url in Dictionary")
        
        #passing "all_course_dict" to "course_categories" method 
        return all_course_dict
    
    def pass_categories_url(self,all_course_dict):
        '''Logic to store our data in list of dict, each dict have all the categories ,subcategories
        and courses details in tree form
        eg:[{categories:
                        {sub_categories:
                                        [[each_course_details],[each_course_details],[..]]} ,
                                        {...}}]
        '''
        
        final_courses_detail=[]
        for course_name,url_list in all_course_dict.items():
            course_insight={}
            t={}
            for j in url_list:
                try:
                    t[j.split('/')[-1]]=self.download_content(j)
                    
                    print("Completed ",j.split('/')[-1]," of course ",course_name)
                except Exception as e:
                    print(e)
                    self.logger.info(f"\"pass_categories_url\" has error {e}")
            course_insight[course_name]=t
            final_courses_detail.append(course_insight)
        return final_courses_detail
    
    
    def download_content(self,url):
        
        '''This will help us to fetch all the courses details and return back to 
        "pass_categories_url"
        '''
        self.driver=webdriver.Chrome(self.driver_path)
        self.driver.get(url)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(page_load_time)
        
        self.attempt=0
        while self.attempt<2:#used while loop to iterate twice incase of webpage timeout error

            try:
                try:
                    fetching_each_course_header=self.driver.find_elements_by_xpath("//h5[@class='Course_course-title__2rA2S']")
                    header_list=[fetching_each_course_header[k].text for k in range(0,len(fetching_each_course_header)) if fetching_each_course_header[k].text!='']
                except NoSuchElementException:
                    header_list=["NO Courses Found"]
                    details_list=["NO Course details Found"]
                    instructor_name_list=["NO Instruction Name"]
                    url_list=['No Course Found']
                    return header_list,details_list,instructor_name_list,url_list
                    break
                    
                    
                try:
                    fetching_each_course_details=self.driver.find_elements_by_xpath("//div[@class='Course_course-desc__2G4h9']")
                    details_list=[fetching_each_course_details[k].text for k in range(0,len(fetching_each_course_details)) if fetching_each_course_details[k].text!='']
                except NoSuchElementException:
                    details_list=["No Course details found"]
                    pass
                
                try:
                    fetching_instructor_name=self.driver.find_elements_by_xpath("//div[@class='Course_course-instructor__1bsVq']")
                    instructor_name_list=[fetching_instructor_name[k].text for k in range(0,len(fetching_instructor_name)) if fetching_instructor_name[k].text!='']
                except NoSuchElementException:
                    instructor_name_list=["NO Instruction name"]
                    pass
                
                url_list=["https://courses.ineuron.ai/"+i.replace(' ','-') for i in header_list]
                self.driver.close()
                l=[list(i) for i in list(zip(header_list,details_list,instructor_name_list,url_list))]
                
                return l
                break
            except Exception as e:
                self.logger.info(f"{url.split('/')[-1]} has thrown exception of {e} trying once again")
                print(url.split('/')[-1]," has thrown exception of ",e," trying once again")
                print("If thrown massage is stale element reference then please increase the page load time")
                self.attempt+=1
    
    
    
driver_path=r"C:\Users\1672040\Desktop\project\Task-main (1)\Task-main\chromedriver_win32\chromedriver.exe"
page_load_time=5 #Adjust the time as per your connection speed

final_content_class_instance=inureon_webscrapping(driver_path,page_load_time)
start=time.time()
final_content=final_content_class_instance.course_categories()
end=time.time()
print(end-start)
print(final_content)


client = pymongo.MongoClient("mongodb+srv://ashishshukla23sep:<password>@cluster0.o1yzz.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db1=client["inureon"]
col1=db1['inureon_webscrapping']
col1.insert_many(final_content)