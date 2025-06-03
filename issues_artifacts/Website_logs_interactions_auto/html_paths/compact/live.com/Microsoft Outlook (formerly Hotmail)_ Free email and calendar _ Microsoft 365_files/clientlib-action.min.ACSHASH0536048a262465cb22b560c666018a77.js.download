/**
* This function is to add source parameter through JS in the hyperlink.
*/
$(document).ready(function () {
    const appendReferrerLinks = document.querySelectorAll('[data-isautoappendreferrer="true"]');
    if (appendReferrerLinks.length) {
        const lang = "/" + document.documentElement.lang?.toLowerCase();
        let currentUrl = window.location.href.toLowerCase().replace(window.location.search, "").replace(lang, "");
        if (currentUrl.endsWith("/")) {
        	currentUrl = currentUrl.slice(0, -1);
        }
        const sourceLink = "srcurl=" + encodeURIComponent(currentUrl);
        appendReferrerLinks.forEach(link => {
            if (!link.href.includes("srcurl=")) {
                const separator = link.href.includes("?") ? "&" : "?";
                link.href = link.href + separator + sourceLink;
            }
        });
    }
});
/**
 * Query Parameter Passthrough Utility
 *
 * This utility updates anchor tags in a web page by modifying the
 * 'href' attributes with the value of the query parameters from the current page URL 
 * based on the authoring of "Query parameter passthru" field in component dialog. 
 * It updates the anchor tags having the data attribute 'data-queryparam-passthru'.
 */
(function (document) {
  /**
   * Parses query parameters from the current page URL.
   * @returns {Object} Parsed query parameters.
   */
  const parseQueryParams = () => {
    let queryParams = {};
    const urlParams = new URLSearchParams(window.location.search);

    urlParams.forEach((value, key) => {
      queryParams[key.toLowerCase()] = value;
    });

    return queryParams; 
  };

  /**
   * Processes anchor tags to update the href attribute with the query parameters 
   * identified by the data attribute('data-queryparam-passthru').
   * @param {NodeList} links - A collection of anchor tags with the data attribute.
   */
  const processAnchorTags = (links) => {
    const queryParams = parseQueryParams();

    links.forEach((link) => {
      const passthruParams = link.dataset.queryparamPassthru.split(",");
      const [ urlBase, urlParams ] = link.getAttribute("href").toLowerCase().split("?");

      let searchParams = new URLSearchParams(urlParams);
      passthruParams.forEach((param) => {
        param = param.trim().toLowerCase();
        if (queryParams[param]) {
          searchParams.set(param, queryParams[param]);
        }
      });

      if (searchParams.toString().length > 0) {
        link.href = `${urlBase}?${searchParams.toString()}`;
      }
    });
  };

  document.addEventListener("DOMContentLoaded", () => {
    const links = document.querySelectorAll("a[data-queryparam-passthru]");
    if (links.length > 0) {
      processAnchorTags(links); 
    }
  });
})(document);

/**
* This function is to open the respective trial scenario modal for the new-trial element.
*/
(function (document) {

    // Create custom new-trial element and bind try for free buttons.
    const trialBindingAttr = 'new-trial-web-component-trigger';
    
    // Add event listener to fire modal
    const bindBizappsNewTrialEvents = () => {
        const newTrialElements = document.querySelectorAll("new-trial"); 

        newTrialElements.forEach(nte => {
            nte.getUserInfo = getUserInfo;
            nte.getProteanToken = getProteanToken;
        });

        const newTrialTriggers = document.querySelectorAll(`[${trialBindingAttr}]`);
        newTrialTriggers.forEach(el => {
            el.addEventListener('click', (e) => {
                e.preventDefault();
                const target = e.currentTarget;
                document.querySelectorAll(`#${target.getAttribute(trialBindingAttr)}`).forEach(modal => {
                    if (typeof modal.openDialogOnClick === 'function') {
                        modal.openDialogOnClick(e);
                    }
                });
            });
        });
        
        // Load web component
        if (newTrialTriggers.length > 0) {
            const script = document.createElement('script');
            script.src = newTrialElements[0].dataset.newtrialjs;
            script.type = 'module';
            script.onload = () => {
                console.log('Script loaded successfully');
            };
        
            script.onerror = ()=>{
                console.log('Error occurred while loading script');
            };
            document.body.appendChild(script);
        }
    };

    const getUserInfo = () => {
        return window.msauth ? {
            firstName: window.msauth.FirstName,
            lastName: window.msauth.LastName,
            emailAddress: window.msauth.EmailAddress,
            tenantId: window.msauth.TenantId
        } : null
    };
      
    const getProteanToken = () => {
        return window.msauth ? {
            token: window.msauth.AuthTicket
        } : null
    };

    // Initialize new trial elements on page load
    document.addEventListener("DOMContentLoaded", bindBizappsNewTrialEvents);

    // Add event listener to rebind new trial events when the market selector is refreshed
    document
        .querySelector("[data-mount='market-selector']")
        ?.addEventListener("onRefreshed", () =>
            setTimeout(bindBizappsNewTrialEvents, 1000)
    );

})(document);

(function(document) {

    let partnerDetailPageLinks;
    let profilerFormData;

    /**
     * Initializes the local storage utility based on the partner detail page type.
     */
    const initializeLocalStorageUtil = () => {
        const trialType = partnerDetailPageLinks[0].dataset.trialtype;
        const storageKey = `${trialType}-profiler`;
        const localStorageUtil = new LocalStorageUtil({
            storageKey
        });
        profilerFormData = getLocalStorageData(localStorageUtil);
    }

    /**
     * Retrieves profiler form data from local storage.
     * @param {LocalStorageUtil} localStorageUtil - The local storage utility instance.
     */
    const getLocalStorageData = (localStorageUtil) => {
        return localStorageUtil.getItem('profilerFormData') || [];
    }

    /**
     * Processes the start trial link by updating its URL with profiler data.
     */
    const processStartTrialLink = (partnerDetailPageLink) => {
        const startTrialUrl = partnerDetailPageLink.href;
        const startTrialUrlDecoded = decodeURIComponent(decodeURIComponent(startTrialUrl));
        const signupContext = extractSignupContext(startTrialUrlDecoded);
        const profilerData = Object.values(profilerFormData).reduce((profilerDataAccumulator, question) => {
            const questionLabel = question.questionLabel.toLowerCase();
            profilerDataAccumulator[questionLabel] = readProfilerSelection(questionLabel);
            return profilerDataAccumulator;
        }, {});
        Object.assign(signupContext, profilerData);
        const updatedStartTrial = buildUpdatedStartTrialUrl(startTrialUrlDecoded, signupContext);
        partnerDetailPageLink.href = updatedStartTrial;
    }

    /**
     * Reads the profiler selection for a given question label.
     * @param {string} questionLabel - The label of the profiler question.
     * @returns {string} The selected profiler options joined by commas.
     */
    const readProfilerSelection = (questionLabel) => {
        const matchingQuestion = Object.values(profilerFormData).find(
            question => question.questionLabel.toLowerCase() === questionLabel.toLowerCase()
        );
        return matchingQuestion?.answer.map(ans => ans.value).join(', ') || '';
    };

    /**
     * Extracts signup context from the decoded start trial URL.
     * @param {string} startTrialUrlDecoded - The decoded start trial URL.
     * @returns {object} The parsed signup context object.
     */
    const extractSignupContext = (startTrialUrlDecoded) => {
        return JSON.parse(startTrialUrlDecoded.split('signupContext=')[1]);
    };

    /**
     * Builds an updated start trial URL with the encoded signup context.
     * @param {string} startTrialUrlDecoded - The decoded start trial URL.
     * @param {object} signupContext - The signup context object.
     * @returns {string} The updated start trial URL.
     */
    const buildUpdatedStartTrialUrl = (startTrialUrlDecoded, signupContext) => {
        const encodedSignupContext = encodeURIComponent(JSON.stringify(signupContext));
        const returnUrl = startTrialUrlDecoded.split('ru=')[1];
        if (returnUrl) {
            const ruParam = encodeURIComponent(`${returnUrl.split('signupContext=')[0]}signupContext=`) + encodeURIComponent(encodedSignupContext);
            return `${startTrialUrlDecoded.split('ru=')[0]}ru=${ruParam}`;
        } else {
            return `${startTrialUrlDecoded.split('signupContext=')[0]}signupContext=${encodedSignupContext}`;
        }
    };

    /**
     * Event listener for the DOMContentLoaded event.
     */
    document.addEventListener("DOMContentLoaded", () => {
        partnerDetailPageLinks = document.querySelectorAll('[data-partner-page="partner-details-page"]');

        if (partnerDetailPageLinks.length > 0) {
            initializeLocalStorageUtil();
            partnerDetailPageLinks.forEach((partnerDetailPageLink) => {
               processStartTrialLink(partnerDetailPageLink);
            });
        }
    });
})(document);
