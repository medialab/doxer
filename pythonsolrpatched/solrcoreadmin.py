from pysolr import Solr
import urllib
import json

class CoreNotStartedException(Exception): pass

class SolrCoreAdminException(Exception):
    def __init__(self,http_code):
        self.http_code = http_code
    def __str__(self):
        return self(self.http_code)

### multicore commands
class SolrCoreAdmin(object):
    """
    Class to support Solr's multicore admin commands
    """
    def __init__(self,url='http://127.0.0.1:8983/solr/',solr_class=Solr):
        self.url = url
        self.core_admin_url = self.url + 'admin/cores?'
        self.solr_class = solr_class
        
    def list_cores(self,name=None):
        if name:
            status_cmd = self.core_admin_url + urllib.urlencode({'action':'status','core':name,'wt':'json'})
        else:
            status_cmd = self.core_admin_url + urllib.urlencode({'action':'status','wt':'json'})
        
        res =  urllib.urlopen(status_cmd)
        data = json.loads(res.read())

        http_code = data['responseHeader']['status']
        if http_code != 0: raise SolrCoreAdminException(http_code)
        
        st = data['status']
        if name:
            if st[name] == {} : return []
        cores = []
        for core_name in st:
            url = "%s%s" %(self.url ,core_name)
            core = self.solr_class(url=url)
            cores.append(core)
        return cores
    
    def create_core(self,name):
        """Create a core. If it already exists, do nothing """
        core = self.list_cores(name)
        if len(core)>0: return

        create_cmd = self.core_admin_url + urllib.urlencode({'action':'create','name':name,'loadOnStart':'false', 'instanceDir':'.','schema':'schema.xml'})
        res =  urllib.urlopen(create_cmd)
               
    def get_core(self,name):
        cores = self.list_cores(name)
        assert len(cores) == 1
        return cores[0]
        
    def is_core_active(self,name): 
        core = self.list_cores(name)
        return len(core) == 1

    def unload_core(self,name):
        core = self.get_core(name)

        unload_cmd = self.core_admin_url + urllib.urlencode({'action':'unload','core':name,'wt':'json'})
        res =  urllib.urlopen(unload_cmd)
        
        return True