injectHeadCodeOnPage = (e) => {
  let n = document.createElement("script");
  n.type = "text/javascript";
  n.async = true;
  n.src = e;
  document.getElementsByTagName("head")[0].appendChild(n);
};
loadGA = (code) => {
  let ga_url = `https://www.googletagmanager.com/gtag/js?id=${code}`;
  injectHeadCodeOnPage(ga_url);
  (window.dataLayer = window.dataLayer || []),
    (window.gtag = function () {
      window.dataLayer.push(arguments);
    });
  window.gtag("js", new Date());
  window.gtag("config", code);
};
loadGA("G-NFN218243Z"); //to load GA code and count pageviews

// //adx code starts //comment this code if you want to run adsense
let gptjsurl = "https://securepubads.g.doubleclick.net/tag/js/gpt.js";

injectHeadCodeOnPage(gptjsurl); //addded gpt.js

window.unibots = window.unibots || { cmd: [] }; // defining googletag fun
var IR_UB;
var IR_UB_300x250; //FROM UB this should be removed
var IR_UB_300x250_2; //FROM UB this should be removed
var IR_UB_NEW;
var IR_STICKY; //FROM UB this should be removed
var IR_300x250_IFRAME; //FROM UB this should be removed
var Adunit_IR_UB_320x50; //FROM UB: This value should be changed as instructed by the UB team
var Adunit_IR_UB_300x250; //FROM UB: This value should be changed as instructed by the UB team
var isSplashScreenOpen = false;
var isTrainList = false;
var isInnerAdPushed = false;
var adunitData; // variable to store adunits
//Fetches the latest ad units for convenient updates without modifying the live code; uses a fetch request to retrieve the JSON

function getAdunitNames() {
  const adunit_data_url = "https://cdn.unibotscdn.com/headerbidding/irctc.json";

  return fetch(adunit_data_url)
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      adunitData = data;
      return adunitData;
    })
    .catch((error) => {
      console.error("Error fetching data:", error);
    });
}

getAdunitNames();

// mobilecheck fun
const isMob = () => {
  if (
    navigator.userAgent.match(/Android/i) ||
    navigator.userAgent.match(/webOS/i) ||
    navigator.userAgent.match(/iPhone/i) ||
    navigator.userAgent.match(/iPad/i) ||
    navigator.userAgent.match(/iPod/i) ||
    navigator.userAgent.match(/BlackBerry/i) ||
    navigator.userAgent.match(/Windows Phone/i)
  ) {
    return true;
  } else {
    return false;
  }
};
let isMobile = isMob();

// below function to define homepage adunts
const defineGPTslots = (all,
  //  Adunit_IR_UB_300x250, 
   Adunit_IR_UB_320x50
  ) => {
  window.googletag = window.googletag || { cmd: [] };
  googletag.cmd.push(function () {
  //   if (all && !isMobile) { //comment this if block to remove 300x250_chatbot slot defination
  //     IR_UB_NEW = googletag
  //       .defineSlot(
  //         Adunit_IR_UB_300x250,
  //         [300, 250],
  //         "div-gpt-ad-1695628300486-0"
  //       )
  //       .addService(googletag.pubads());
  //   }

    IR_UB = googletag
      .defineSlot(Adunit_IR_UB_320x50, [320, 50], "div-gpt-ad-1695628181945-0")
      .addService(googletag.pubads());
    googletag.pubads().enableSingleRequest();
    googletag.enableServices();
  });
};
//function to define slots for homepage adunits
if (!adunitData && adunitData == undefined) {
  getAdunitNames()
    .then((adunitData) => {
      defineGPTslots(
        true,
      //   adunitData["Adunit_IR_UB_300x250"],
        adunitData["Adunit_IR_UB_320x50"]
      );
    })
    .catch((err) => {
      console.log(err);
    });
} else {
  defineGPTslots(
    true,
  //   adunitData["Adunit_IR_UB_300x250"],
    adunitData["Adunit_IR_UB_320x50"]
  );
}

//function for train-list page adunit 300x250
function pushInnerAd(Adunit_IR_UB_TS_300x250) {
  const isMobileCheck = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
  if (
    window.location.href.includes("nget/booking/train-list") &&
    !isMobileCheck
  ) {
    isTrainList = true;
    isInnerAdPushed = true;

    googletag.cmd.push(function () {
      googletag
        .defineSlot(
          Adunit_IR_UB_TS_300x250,
          [300, 250],
          "div-gpt-ad-1698143516599-0"
        )
        .addService(googletag.pubads());
      googletag.pubads().enableSingleRequest();
      googletag.enableServices();
    });
    //Element creation for inner Ad
    var filterDiv = document.querySelector(".filter-div");
    let innerAd = document.createElement("div");
    innerAd.style.width = "300px";
    innerAd.style.height = "250px";
    innerAd.style.margin = "auto";
    innerAd.style.display = "block !important";
    innerAd.style.cssText =
      "display: block !important; background-image: url(https://cdn.jsdelivr.net/gh/corover/assets@a1/askdisha-bucket/300_250.png);background-origin: content-box;background-repeat: no-repeat;background-size: contain !important;display:block !important; width:300px;height:250px; margin-top:20px";
    innerAd.id = "div-gpt-ad-1698143516599-0";
    filterDiv.appendChild(innerAd);

    const targetDivId = "div-gpt-ad-1698143516599-0";
    const interval = setInterval(() => {
      const targetDiv = document.getElementById(targetDivId);
      if (targetDiv) {
        clearInterval(interval);
        googletag.cmd.push(function () {
          googletag.display("div-gpt-ad-1698143516599-0");
        });
      } else console.log("Div " + targetDivId + " not found yet...");
    }, 100);

    // Start checking for the div when the script runs

    console.log("5: ", isTrainList, " 6: ", isInnerAdPushed);
  } else {
    isTrainList = false;
  }
}
//reload function when initial req didn't work
const reloadADs = (all) => {
  if (!adunitData && adunitData !== undefined) {
    getAdunitNames()
      .then((adunitData) => {
        defineGPTslots(
          all,
          // adunitData["Adunit_IR_UB_300x250"],
          adunitData["Adunit_IR_UB_320x50"]
        );
      })
      .catch((err) => {
        console.error(err);
      });
  } else {
    defineGPTslots(
      all,
      // adunitData["Adunit_IR_UB_300x250"],
      adunitData["Adunit_IR_UB_320x50"]
    );
  }
  //display sticky ad
  googletag.cmd.push(function () {
    googletag.display("div-gpt-ad-1695628181945-0");
  });
  //display inbot ad
  // if (all && !isMobile) {
  //   googletag.cmd.push(function () {
  //     googletag.display("div-gpt-ad-1695628300486-0");
  //   });
  // }
};

let oldUrl = window.location.href;

//sending request and call fun for train-list adunits
window.addEventListener("click", function () {
  setTimeout(() => {
    if (window.location.href != oldUrl) {
      let s = !isMobile;
      if (!window.location.href.includes("nget/booking/train-list")) {
        reloadADs(s);
      }
      // else {
      //   if (!adunitData && adunitData !== undefined) {
      //     fetchAdunitData()
      //       .then(() => {
      //         pushInnerAd(adunitData["Adunit_IR_UB_TS_300x250"]);
      //       })
      //       .catch((err) => {
      //         console.error(err);
      //       });
      //   } else {
      //     pushInnerAd(adunitData["Adunit_IR_UB_TS_300x250"]);
      //   }
      // }
      isTrainList = false;
      oldUrl = window.location.href;
    }
  }, 2000);
});
//function to send initial ad request
const runNewDisplayAd = () => {
  googletag.cmd.push(function () {
    googletag.display("div-gpt-ad-1695628181945-0");
  });
  // if (!isMobile) {   //comment this if block to stop 300x250_chatbot request
  //   googletag.cmd.push(function () {
  //     googletag.display("div-gpt-ad-1695628300486-0");
  //   });
  // }
};
//function to refresh  ads
function refreshHomeAdWindow() {
  googletag.cmd.push(function () {
    if (!isMobile) {
      googletag.pubads().refresh([IR_UB_NEW]);
    }
    googletag.pubads().refresh([IR_UB]);
  });
}

setTimeout(() => {
  runNewDisplayAd();
}, 2000);

setInterval(() => {
  if (!window.location.href.includes("nget/booking/train-list")) {
    refreshHomeAdWindow();
  }
}, 35000);
// //adx code ends // comment adx code till here if you want to run adsense



//adsense code starts - COMMENT ALL CODE ABOVE except the loadGA() function to run adsense on the site and remove adx and vice versa
//adsense head code starts

// let ub_script1 = document.createElement("script");
// ub_script1.async = "async";
// ub_script1.src =
//   "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5761017298734489";
// ub_script1.setAttribute("crossorigin", "anonymous");
// document.getElementsByTagName("head")[0].appendChild(ub_script1);

//adsense head code ends

//sticky_320x50 starts

//   let ub_anchordiv = document.createElement("ins");
//   ub_anchordiv.setAttribute("class", "adsbygoogle");
//   ub_anchordiv.setAttribute("data-ad-client", "ca-pub-5761017298734489");
//   ub_anchordiv.setAttribute("data-ad-slot", "5481682884");
//   let tardiv1 = document.querySelector("#div-gpt-ad-1695628181945-0");
//   if(tardiv1){
//   tardiv1.appendChild(ub_anchordiv);
//   }
//   (adsbygoogle = window.adsbygoogle || []).push({});

//sticky_320x50 ends

//chatbot_300x250 starts

// let ub_chatBotdiv = document.createElement("ins");
// ub_chatBotdiv.setAttribute("class", "adsbygoogle");
// ub_chatBotdiv.setAttribute("data-ad-client", "ca-pub-5761017298734489");
// ub_chatBotdiv.setAttribute("data-ad-slot", "2913012258");
// let tardiv2 = document.querySelector("#div-gpt-ad-1695628300486-0");
// if(tardiv2){
// tardiv2.appendChild(ub_chatBotdiv);
// }
// (adsbygoogle = window.adsbygoogle || []).push({});

//chatbot_300x250 ends
//adsense code ends