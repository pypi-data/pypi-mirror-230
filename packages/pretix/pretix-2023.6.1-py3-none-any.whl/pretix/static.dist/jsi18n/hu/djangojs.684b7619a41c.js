

'use strict';
{
  const globals = this;
  const django = globals.django || (globals.django = {});

  
  django.pluralidx = function(n) {
    const v = n != 1;
    if (typeof v === 'boolean') {
      return v ? 1 : 0;
    } else {
      return v;
    }
  };
  

  /* gettext library */

  django.catalog = django.catalog || {};
  
  const newcatalog = {
    "(one more date)": [
      "(m\u00e9g egy id\u0151pont)",
      "(m\u00e9g {num} id\u0151pont)"
    ],
    "All": "\u00d6sszes",
    "An error has occurred.": "Hiba l\u00e9pett fel.",
    "An error of type {code} occurred.": "{code} t\u00edpus\u00fa hiba jelentkezett.",
    "April": "\u00c1prilis",
    "August": "Augusztus",
    "Barcode area": "Vonalk\u00f3d ter\u00fclet",
    "Calculating default price\u2026": "Alap\u00e9rtelmezett \u00e1r kalkul\u00e1l\u00e1sa\u2026",
    "Cart expired": "A kos\u00e1r lej\u00e1rt",
    "Check-in QR": "Check in QR",
    "Click to close": "Bez\u00e1r\u00e1s\u00e9rt kattints",
    "Close message": "\u00dczenet bez\u00e1r\u00e1sa",
    "Comment:": "Megjegyz\u00e9s:",
    "Confirming your payment \u2026": "A fizet\u00e9s meger\u0151s\u00edt\u00e9se\u2026",
    "Contacting Stripe \u2026": "Kapcsolatfelv\u00e9tel Stripe-pal\u2026",
    "Contacting your bank \u2026": "Kapcsolatfelv\u00e9tel a bankj\u00e1val\u2026",
    "Copied!": "M\u00e1solva!",
    "Count": "Sz\u00e1m\u00edt\u00e1s",
    "December": "December",
    "Do you really want to leave the editor without saving your changes?": "Biztosan ki akar l\u00e9pni a szerkeszt\u0151b\u0151l a v\u00e1ltoztat\u00e1sok ment\u00e9se n\u00e9lk\u00fcl?",
    "Error while uploading your PDF file, please try again.": "Hiba a PDF f\u00e1jl felt\u00f6lt\u00e9se k\u00f6zben, pr\u00f3b\u00e1lja \u00fajra.",
    "February": "Febru\u00e1r",
    "Fr": "P",
    "Generating messages \u2026": "\u00dczenetek gener\u00e1l\u00e1sa\u2026",
    "Group of objects": "t\u00e1rgy csoport",
    "January": "Janu\u00e1r",
    "July": "J\u00falius",
    "June": "J\u00fanius",
    "March": "M\u00e1rcius",
    "Marked as paid": "Fizetettnek jel\u00f6lt",
    "May": "M\u00e1jus",
    "Mo": "H",
    "No": "Nem",
    "None": "Semmi",
    "November": "November",
    "Object": "objektum",
    "October": "Okt\u00f3ber",
    "Others": "Egy\u00e9b",
    "Paid orders": "Kifizetett megrendel\u00e9sek",
    "Placed orders": "Megrendel\u00e9sek",
    "Please enter a quantity for one of the ticket types.": "Adjon meg egy mennyis\u00e9get az egyik jegyt\u00edpusb\u00f3l.",
    "Powered by pretix": "pretix \u00e1ltal m\u0171k\u00f6dtetett",
    "Press Ctrl-C to copy!": "Nyomjon Ctrl+C-t a m\u00e1sol\u00e1shoz!",
    "Sa": "Szo",
    "Saving failed.": "Ment\u00e9s sikertelen.",
    "September": "Szeptember",
    "Su": "V",
    "Text object": "Sz\u00f6veg",
    "Th": "Cs",
    "The PDF background file could not be loaded for the following reason:": "A PDF h\u00e1tt\u00e9r f\u00e1jl nem t\u00f6lthet\u0151 be a k\u00f6vetkez\u0151k miatt:",
    "The request took too long. Please try again.": "A k\u00e9r\u00e9s id\u0151t\u00fall\u00e9p\u00e9s miatt le\u00e1llt. K\u00e9rj\u00fck pr\u00f3b\u00e1lja \u00fajra.",
    "Ticket design": "Jegy design",
    "Total": "Teljes",
    "Total revenue": "Teljes bev\u00e9tel",
    "Tu": "K",
    "Unknown error.": "Ismeretlen hiba.",
    "Use a different name internally": "Haszn\u00e1lj m\u00e1sik nevet",
    "We": "Sze",
    "We are currently sending your request to the server. If this takes longer than one minute, please check your internet connection and then reload this page and try again.": "A k\u00e9relem tov\u00e1bb\u00edt\u00e1sa a kiszolg\u00e1l\u00f3 fel\u00e9 folyamatban. Ha ez egy percn\u00e9l hosszabb id\u0151t vesz ig\u00e9nybe, k\u00e9rj\u00fck ellen\u0151rizze az internetkapcsolat\u00e1t, friss\u00edtse az oldalt \u00e9s pr\u00f3b\u00e1lkozzon \u00fajra.",
    "We are processing your request \u2026": "A k\u00e9r\u00e9s feldolgoz\u00e1sa folyamatban\u2026",
    "We currently cannot reach the server, but we keep trying. Last error code: {code}": "Jelen pillanatban a kiszolg\u00e1l\u00f3 nem el\u00e9rhet\u0151, de tov\u00e1bbra is pr\u00f3b\u00e1lkozunk. Utols\u00f3 hibak\u00f3d: {code}",
    "We currently cannot reach the server. Please try again. Error code: {code}": "Jelen pillanatban a kiszolg\u00e1l\u00f3 nem el\u00e9rhet\u0151. Pr\u00f3b\u00e1lja \u00fajra. Hibak\u00f3d: {code}",
    "Yes": "Igen",
    "You have unsaved changes!": "Mentetlen v\u00e1ltoztat\u00e1sok!",
    "Your color has bad contrast for text on white background, please choose a darker shade.": "A v\u00e1lasztott sz\u00ednek kontrasztja el\u00e9gtelen, k\u00e9rj\u00fck v\u00e1lassz s\u00f6t\u00e9tebb \u00e1rnyalatot.",
    "Your color has decent contrast and is probably good-enough to read!": "A v\u00e1lasztott sz\u00ednek kontrasztja el\u00e9gs\u00e9ges, \u00e9s val\u00f3sz\u00edn\u0171leg j\u00f3l olvashat\u00f3!",
    "Your color has great contrast and is very easy to read!": "A v\u00e1lasztott sz\u00ednek remek kontrasztot adnak, \u00e9s nagyon k\u00f6nny\u0171 olvasni!",
    "Your request arrived on the server but we still wait for it to be processed. If this takes longer than two minutes, please contact us or go back in your browser and try again.": "A k\u00e9r\u00e9s meg\u00e9rkezett a kiszolg\u00e1l\u00f3hoz, a feldolgoz\u00e1sra v\u00e1rni kell. Ha ez a folyamat k\u00e9t percn\u00e9l hosszabb ideg tart, k\u00e9rj\u00fck vegye fel vel\u00fcnk a kapcsolatot, vagy l\u00e9pjen vissza a b\u00f6ng\u00e9sz\u0151j\u00e9ben \u00e9s pr\u00f3b\u00e1lja \u00fajra.",
    "widget\u0004Back": "Vissza",
    "widget\u0004Buy": "V\u00e1s\u00e1rl\u00e1s",
    "widget\u0004Choose a different date": "M\u00e1sik id\u0151pont v\u00e1laszt\u00e1sa",
    "widget\u0004Choose a different event": "M\u00e1sik esem\u00e9ny v\u00e1laszt\u00e1sa",
    "widget\u0004Close": "Bez\u00e1r\u00e1s",
    "widget\u0004Close ticket shop": "Jegyv\u00e1s\u00e1rl\u00e1s bez\u00e1r\u00e1sa",
    "widget\u0004Continue": "Folytat\u00e1s",
    "widget\u0004FREE": "INGYENES",
    "widget\u0004Next month": "K\u00f6vetkez\u0151 h\u00f3nap",
    "widget\u0004Only available with a voucher": "Csak kuponnal el\u00e9rhet\u0151",
    "widget\u0004Open seat selection": "Helyv\u00e1laszt\u00e1s megnyit\u00e1sa",
    "widget\u0004Previous month": "El\u0151z\u0151 h\u00f3nap",
    "widget\u0004Redeem": "Bev\u00e1lt\u00e1s",
    "widget\u0004Redeem a voucher": "Kupon bev\u00e1lt\u00e1sa",
    "widget\u0004Register": "Regisztr\u00e1ci\u00f3",
    "widget\u0004Reserved": "Foglalt",
    "widget\u0004Resume checkout": "Fizet\u00e9s folytat\u00e1sa",
    "widget\u0004See variations": "Vari\u00e1ci\u00f3k mutat\u00e1sa",
    "widget\u0004Sold out": "Elkelt",
    "widget\u0004The cart could not be created. Please try again later": "A kos\u00e1r fel\u00f6lt\u00e9se sikertelen. K\u00e9rj\u00fck pr\u00f3b\u00e1lja \u00fajra",
    "widget\u0004The ticket shop could not be loaded.": "Jegyv\u00e1s\u00e1rl\u00e1s bet\u00f6lt\u00e9se sikertelen.",
    "widget\u0004Voucher code": "Kupon k\u00f3d",
    "widget\u0004Waiting list": "V\u00e1r\u00f3lista",
    "widget\u0004You currently have an active cart for this event. If you select more products, they will be added to your existing cart.": "A rendezv\u00e9nyhez m\u00e1r tartozik kos\u00e1rtartalom. a tov\u00e1bbi kijel\u00f6lt term\u00e9keket a m\u00e1r megl\u00e9v\u0151 kos\u00e1rhoz adjuk.",
    "widget\u0004currently available: %s": "jelenleg el\u00e9rhet\u0151: %s",
    "widget\u0004from %(currency)s %(price)s": "%(currency) %(price)-t\u00f3l",
    "widget\u0004incl. %(rate)s% %(taxname)s": "bele\u00e9rtve %(rate)% %(taxname)",
    "widget\u0004incl. taxes": "ad\u00f3val",
    "widget\u0004minimum amount to order: %s": "minim\u00e1lis rendel\u00e9s: %s",
    "widget\u0004plus %(rate)s% %(taxname)s": "plusz %(rate)% %(taxname)",
    "widget\u0004plus taxes": "plusz j\u00e1rul\u00e9kok"
  };
  for (const key in newcatalog) {
    django.catalog[key] = newcatalog[key];
  }
  

  if (!django.jsi18n_initialized) {
    django.gettext = function(msgid) {
      const value = django.catalog[msgid];
      if (typeof value === 'undefined') {
        return msgid;
      } else {
        return (typeof value === 'string') ? value : value[0];
      }
    };

    django.ngettext = function(singular, plural, count) {
      const value = django.catalog[singular];
      if (typeof value === 'undefined') {
        return (count == 1) ? singular : plural;
      } else {
        return value.constructor === Array ? value[django.pluralidx(count)] : value;
      }
    };

    django.gettext_noop = function(msgid) { return msgid; };

    django.pgettext = function(context, msgid) {
      let value = django.gettext(context + '\x04' + msgid);
      if (value.includes('\x04')) {
        value = msgid;
      }
      return value;
    };

    django.npgettext = function(context, singular, plural, count) {
      let value = django.ngettext(context + '\x04' + singular, context + '\x04' + plural, count);
      if (value.includes('\x04')) {
        value = django.ngettext(singular, plural, count);
      }
      return value;
    };

    django.interpolate = function(fmt, obj, named) {
      if (named) {
        return fmt.replace(/%\(\w+\)s/g, function(match){return String(obj[match.slice(2,-2)])});
      } else {
        return fmt.replace(/%s/g, function(match){return String(obj.shift())});
      }
    };


    /* formatting library */

    django.formats = {
    "DATETIME_FORMAT": "Y. F j. H:i",
    "DATETIME_INPUT_FORMATS": [
      "%Y.%m.%d. %H:%M:%S",
      "%Y.%m.%d. %H:%M:%S.%f",
      "%Y.%m.%d. %H:%M",
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%Y-%m-%d"
    ],
    "DATE_FORMAT": "Y. F j.",
    "DATE_INPUT_FORMATS": [
      "%Y.%m.%d.",
      "%Y-%m-%d"
    ],
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": 1,
    "MONTH_DAY_FORMAT": "F j.",
    "NUMBER_GROUPING": 3,
    "SHORT_DATETIME_FORMAT": "Y.m.d. H:i",
    "SHORT_DATE_FORMAT": "Y.m.d.",
    "THOUSAND_SEPARATOR": "\u00a0",
    "TIME_FORMAT": "H:i",
    "TIME_INPUT_FORMATS": [
      "%H:%M:%S",
      "%H:%M",
      "%H:%M:%S.%f"
    ],
    "YEAR_MONTH_FORMAT": "Y. F"
  };

    django.get_format = function(format_type) {
      const value = django.formats[format_type];
      if (typeof value === 'undefined') {
        return format_type;
      } else {
        return value;
      }
    };

    /* add to global namespace */
    globals.pluralidx = django.pluralidx;
    globals.gettext = django.gettext;
    globals.ngettext = django.ngettext;
    globals.gettext_noop = django.gettext_noop;
    globals.pgettext = django.pgettext;
    globals.npgettext = django.npgettext;
    globals.interpolate = django.interpolate;
    globals.get_format = django.get_format;

    django.jsi18n_initialized = true;
  }
};

