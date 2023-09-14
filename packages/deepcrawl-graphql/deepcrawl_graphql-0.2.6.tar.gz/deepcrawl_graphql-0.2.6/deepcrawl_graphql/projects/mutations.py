from deepcrawl_graphql.api import DeepCrawlConnection
from deepcrawl_graphql.projects.fields import ProjectFields


class ProjectMutation:
    def __init__(self, conn: DeepCrawlConnection) -> None:
        self.conn = conn
        self.ds = conn.ds
        self.mutation = self.ds.Mutation

    def create_project(self, project_input, fields=None):
        """Creates a Project

        .. dropdown:: GraphQL Input Example

            It has to be converted to dict

            .. code-block::

                input CreateProjectInput {
                  accountId: ObjectID!
                  alertEmails: [String!]
                  alertSettingCode: AlertSettingCode! = Always
                  apiCallbackHeaders: [APICallbackHeaderInput!]! = []
                  apiCallbackUrl: String = null
                  autoFinalizeOnCrawlLimits: Boolean! = false
                  compareToCrawl: CompareToCrawlType! = LastCrawl
                  crawlDisallowedUrls1stLevel: Boolean! = false
                  crawlHyperlinksExternal: Boolean! = false
                  crawlHyperlinksInternal: Boolean! = true
                  crawlImagesExternal: Boolean! = false
                  crawlImagesInternal: Boolean! = true
                  crawlNofollowHyperlinks: Boolean! = true
                  crawlNonHtml: Boolean! = false
                  crawlNotIncluded1stLevel: Boolean! = false
                  crawlRedirectsExternal: Boolean! = true
                  crawlRedirectsInternal: Boolean! = true
                  crawlRelAmphtmlExternal: Boolean! = false
                  crawlRelAmphtmlInternal: Boolean! = true
                  crawlRelCanonicalsExternal: Boolean! = false
                  crawlRelCanonicalsInternal: Boolean! = true
                  crawlRelHreflangsExternal: Boolean! = false
                  crawlRelHreflangsInternal: Boolean! = true
                  crawlRelMobileExternal: Boolean! = false
                  crawlRelMobileInternal: Boolean! = true
                  crawlRelNextPrevExternal: Boolean! = false
                  crawlRelNextPrevInternal: Boolean! = true
                  crawlRobotsTxtNoindex: Boolean! = true
                  crawlScriptsExternal: Boolean! = false
                  crawlScriptsInternal: Boolean! = true
                  crawlStylesheetsExternal: Boolean! = false
                  crawlStylesheetsInternal: Boolean! = true
                  crawlTestSite: Boolean! = false
                  crawlTypes: [CrawlType!]! = [Web]
                  customDns: [CustomDnsSettingInput!]! = []
                  customExtractions: [CustomExtractionSettingInput!]! = []
                  customRequestHeaders: [CustomRequestHeaderInput!]! = []
                  discoverSitemapsInRobotsTxt: Boolean! = true
                  duplicatePrecision: Float! = 3
                  emptyPageThreshold: Int! = 512
                  excludeUrlPatterns: [String!]! = []
                  gaDateRange: Int! = 30
                  ignoreInvalidSSLCertificate: Boolean! = false
                  includeHttpAndHttps: Boolean! = false
                  includeSubdomains: Boolean! = false
                  includeUrlPatterns: [String!]! = []
                  industryCode: String
                  limitLevelsMax: Int
                  limitUrlsMax: Int
                  locationCode: LocationCode! = Default
                  logSummaryRequestsHigh: Int! = 100
                  logSummaryRequestsLow: Int! = 10
                  maxBodyContentLength: Int! = 51200
                  maxDescriptionLength: Int! = 230
                  maxFollowedExternalLinks: Int! = 10
                  maxHtmlSize: Int! = 204800
                  maxLinks: Int! = 250
                  maxLoadTime: Float! = 3
                  maxRedirections: Int! = 4
                  maxTitleWidth: Int! = 600
                  maxUrlLength: Int! = 1024
                  maximumCrawlRate: Float! = 3
                  maximumCrawlRateAdvanced: [AdvancedCrawlRateInput!]! = []
                  minDescriptionLength: Int! = 50
                  minTitleLength: Int! = 10
                  minVisits: Int! = 2
                  mobileHomepageUrl: String = null
                  mobileUrlPattern: String = null
                  mobileUserAgentCode: String! = "googlebot-smartphone"
                  name: String!
                  primaryDomain: String!
                  rendererBlockAds: Boolean! = true
                  rendererBlockAnalytics: Boolean! = true
                  rendererBlockCustom: [String!]! = []
                  rendererJsString: String = null
                  rendererJsUrls: [String!]! = []
                  robotsOverwrite: String = null
                  secondaryDomains: [String!]! = []
                  startUrls: [String!]! = []
                  testSiteDomain: String = null
                  testSitePassword: String = null
                  testSiteUsername: String = null
                  thinPageThreshold: Int! = 3072
                  urlRewriteQueryParameters: [String!]! = []
                  urlRewriteRules: [UrlRewriteRuleInput!]! = []
                  urlRewriteStripFragment: Boolean! = true
                  urlSampling: [UrlSamplingInput!]! = []
                  useMobileSettings: Boolean! = false
                  useRenderer: Boolean! = false
                  useRobotsOverwrite: Boolean! = false
                  useStealthMode: Boolean! = false
                  useUrlRewriteRules: Boolean! = false
                  userAgentCode: String! = "googlebot-smartphone"
                  userAgentString: String = null
                  userAgentStringMobile: String = null
                  userAgentToken: String = null
                  userAgentTokenMobile: String = null
                }

        :param project_input: Project input
        :type project_input: dict
        :param fields: Select specific fields
        :type fields: List(DSLField)
        """
        mutation = self.mutation.createProject.args(input=project_input).select(
            self.ds.CreateProjectPayload.project.select(*fields or ProjectFields.fields(self.ds))
        )
        return self.conn.run_mutation(mutation)

    def update_project(self, project_input, fields=None):
        """Updates a Project

        .. dropdown:: GraphQL Input Example

            It has to be converted to dict

            .. code-block::

                input UpdateProjectInput {
                  alertEmails: [String!]
                  alertSettingCode: AlertSettingCode
                  apiCallbackHeaders: [APICallbackHeaderInput!]
                  apiCallbackUrl: String
                  autoFinalizeOnCrawlLimits: Boolean
                  compareToCrawl: CompareToCrawl
                  crawlDisallowedUrls1stLevel: Boolean
                  crawlHyperlinksExternal: Boolean
                  crawlHyperlinksInternal: Boolean
                  crawlImagesExternal: Boolean
                  crawlImagesInternal: Boolean
                  crawlNofollowHyperlinks: Boolean
                  crawlNonHtml: Boolean
                  crawlNotIncluded1stLevel: Boolean
                  crawlRedirectsExternal: Boolean
                  crawlRedirectsInternal: Boolean
                  crawlRelAmphtmlExternal: Boolean
                  crawlRelAmphtmlInternal: Boolean
                  crawlRelCanonicalsExternal: Boolean
                  crawlRelCanonicalsInternal: Boolean
                  crawlRelHreflangsExternal: Boolean
                  crawlRelHreflangsInternal: Boolean
                  crawlRelMobileExternal: Boolean
                  crawlRelMobileInternal: Boolean
                  crawlRelNextPrevExternal: Boolean
                  crawlRelNextPrevInternal: Boolean
                  crawlRobotsTxtNoindex: Boolean
                  crawlScriptsExternal: Boolean
                  crawlScriptsInternal: Boolean
                  crawlStylesheetsExternal: Boolean
                  crawlStylesheetsInternal: Boolean
                  crawlTestSite: Boolean
                  crawlTypes: [CrawlType!]
                  customDns: [CustomDnsSettingInput!]
                  customExtractions: [CustomExtractionSettingInput!]
                  customRequestHeaders: [CustomRequestHeaderInput!]
                  discoverSitemapsInRobotsTxt: Boolean
                  duplicatePrecision: Float
                  emptyPageThreshold: Int
                  excludeUrlPatterns: [String!]
                  gaDateRange: Int
                  ignoreInvalidSSLCertificate: Boolean
                  includeHttpAndHttps: Boolean
                  includeSubdomains: Boolean
                  includeUrlPatterns: [String!]
                  industryCode: String
                  limitLevelsMax: Int
                  limitUrlsMax: Int
                  locationCode: LocationCode
                  logSummaryRequestsHigh: Int
                  logSummaryRequestsLow: Int
                  maxBodyContentLength: Int
                  maxDescriptionLength: Int
                  maxFollowedExternalLinks: Int
                  maxHtmlSize: Int
                  maxLinks: Int
                  maxLoadTime: Float
                  maxRedirections: Int
                  maxTitleWidth: Int
                  maxUrlLength: Int
                  maximumCrawlRate: Float
                  maximumCrawlRateAdvanced: [AdvancedCrawlRateInput!]
                  minDescriptionLength: Int
                  minTitleLength: Int
                  minVisits: Int
                  mobileHomepageUrl: String
                  mobileUrlPattern: String
                  mobileUserAgentCode: String
                  name: String
                  primaryDomain: String
                  projectId: ObjectID!
                  rendererBlockAds: Boolean
                  rendererBlockAnalytics: Boolean
                  rendererBlockCustom: [String!]
                  rendererJsString: String
                  rendererJsUrls: [String!]
                  robotsOverwrite: String
                  secondaryDomains: [String!]
                  startUrls: [String!]
                  testSiteDomain: String
                  testSitePassword: String
                  testSiteUsername: String
                  thinPageThreshold: Int
                  urlRewriteQueryParameters: [String!]
                  urlRewriteRules: [UrlRewriteRuleInput!]
                  urlRewriteStripFragment: Boolean
                  urlSampling: [UrlSamplingInput!]
                  useMobileSettings: Boolean
                  useRenderer: Boolean
                  useRobotsOverwrite: Boolean
                  useStealthMode: Boolean
                  useUrlRewriteRules: Boolean
                  userAgentCode: String
                  userAgentString: String
                  userAgentStringMobile: String
                  userAgentToken: String
                  userAgentTokenMobile: String
                }

        :param project_input: Project input
        :type project_input: dict
        :param fields: Select specific fields
        :type fields: List(DSLField)
        """
        mutation = self.mutation.updateProject.args(input=project_input).select(
            self.ds.UpdateProjectPayload.project.select(*fields or ProjectFields.fields(self.ds))
        )
        return self.conn.run_mutation(mutation)

    def delete_project(self, project_id, fields=None):
        """Deletes a Project

        :param project_id: Project id
        :type project_id: int or str
        :param fields: Select specific fields
        :type fields: List(DSLField)
        """
        mutation = self.mutation.deleteProject.args(projectId=project_id).select(
            self.ds.DeleteProjectPayload.project.select(*fields or ProjectFields.fields(self.ds))
        )
        return self.conn.run_mutation(mutation)
