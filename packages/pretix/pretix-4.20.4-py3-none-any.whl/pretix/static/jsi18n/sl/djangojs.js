

'use strict';
{
  const globals = this;
  const django = globals.django || (globals.django = {});

  
  django.pluralidx = function(n) {
    const v = n%100==1 ? 0 : n%100==2 ? 1 : n%100==3 || n%100==4 ? 2 : 3;
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
      "en",
      "dva",
      "ve\u010d",
      "drugi"
    ],
    "All": "Vse",
    "An error has occurred.": "Pri\u0161lo je do napake.",
    "An error of type {code} occurred.": "Pri\u0161lo je do napake tipa {code}.",
    "April": "April",
    "August": "Avgust",
    "Barcode area": "Podro\u010dje za \u010drtno kodo",
    "Calculating default price\u2026": "Izra\u010dun privzete cene \u2026",
    "Cart expired": "Vsebina ko\u0161arice je potekla",
    "Check-in QR": "QR koda za check-in",
    "Click to close": "Kliknite za zapiranje",
    "Close message": "Zapri obvestilo",
    "Comment:": "Komentar:",
    "Confirming your payment \u2026": "Potrjevanje pla\u010dila \u2026",
    "Contacting Stripe \u2026": "Povezovanje s servisom Stripe \u2026",
    "Contacting your bank \u2026": "Povezovanje z banko \u2026",
    "Copied!": "Prekopirano!",
    "Count": "Se\u0161tevek",
    "December": "December",
    "Do you really want to leave the editor without saving your changes?": "Ali zares \u017eelite zapustiti urejevalnik ne da bi shranili spremembe?",
    "Error while uploading your PDF file, please try again.": "Napaka pri nalaganju datoteke PDF. Poskusite ponovno.",
    "February": "Februar",
    "Fr": "Pet",
    "Generating messages \u2026": "Pripravljam sporo\u010dilo \u2026",
    "Group of objects": "Skupina objektov",
    "January": "Januar",
    "July": "Julij",
    "June": "Junij",
    "March": "Marec",
    "Marked as paid": "Pla\u010dano",
    "May": "Maj",
    "Mo": "Pon",
    "No": "Ne",
    "None": "Ni\u010d",
    "November": "November",
    "Object": "Objekt",
    "October": "Oktober",
    "Others": "Drugi",
    "Paid orders": "Pla\u010dana naro\u010dila",
    "Placed orders": "Oddana naro\u010dila",
    "Please enter a quantity for one of the ticket types.": "Prosimo vnesite koli\u010dino za eno od vrst vstopnic.",
    "Powered by pretix": "Powered by pretix",
    "Press Ctrl-C to copy!": "Za kopiranje pritisnite Ctrl-C!",
    "Sa": "Sob",
    "Saving failed.": "Shranjevanje ni bilo uspe\u0161no.",
    "September": "September",
    "Su": "Ned",
    "Text object": "Tekstovni objekt",
    "Th": "\u010cet",
    "The PDF background file could not be loaded for the following reason:": "Ozadja PDF ni bilo mogo\u010de nalo\u017eiti zaradi naslednjega razloga:",
    "Ticket design": "Oblikovanje vstopnice",
    "Total": "Skupaj",
    "Total revenue": "Skupni prihodek",
    "Tu": "Tor",
    "Unknown error.": "Neznana napaka.",
    "Use a different name internally": "Uporabite drugo interno ime",
    "We": "Sre",
    "We are currently sending your request to the server. If this takes longer than one minute, please check your internet connection and then reload this page and try again.": "Va\u0161o zahtevo smo posredovali na stre\u017enik. \u010ce to traja ve\u010d kot eno minuto, preverite va\u0161o internetno povezavo in nato ponovno nalo\u017eite spletno stran in poskusite znova.",
    "We are processing your request \u2026": "Obdelujemo va\u0161o zahtevo \u2026",
    "We currently cannot reach the server, but we keep trying. Last error code: {code}": "Stre\u017enik trenutno ni dosegljiv, bomo pa \u0161e posku\u0161ali. Zadnja koda napake: {code}",
    "We currently cannot reach the server. Please try again. Error code: {code}": "Stre\u017enik trenutno ni dosegljiv. Poskusite ponovno. Koda napake: {code}",
    "Yes": "Da",
    "Your color has bad contrast for text on white background, please choose a darker shade.": "Va\u0161a barva ima slab kontrast za besedilo na belem ozadju. Izberite temnej\u0161i odtenek.",
    "Your color has decent contrast and is probably good-enough to read!": "Va\u0161a barva ima zadovoljiv kontrast in je berljiva!",
    "Your color has great contrast and is very easy to read!": "Va\u0161a barva ima dober kontrast in je lepo \u010ditljiva!",
    "Your request arrived on the server but we still wait for it to be processed. If this takes longer than two minutes, please contact us or go back in your browser and try again.": "Va\u0161a zahteva je prispela do stre\u017enika a \u0161e vedno \u010dakamo, da se izvede. \u010ce to traja \u017ee ve\u010d kot nekaj minut, nas prosimo kontaktirajte ali pojdite z brskalnikom nazaj in poskusite ponovno.",
    "widget\u0004Back": "Nazaj",
    "widget\u0004Buy": "Kupi",
    "widget\u0004Choose a different date": "Izberite drug datum",
    "widget\u0004Choose a different event": "Izberite drug dogodek",
    "widget\u0004Close": "Zapri",
    "widget\u0004Close ticket shop": "Zapri trgovino z vstopnicami",
    "widget\u0004Continue": "Nadaljuj",
    "widget\u0004FREE": "Brezpla\u010dno",
    "widget\u0004Next month": "Naslednji mesec",
    "widget\u0004Only available with a voucher": "Na voljo samo z vav\u010derjem",
    "widget\u0004Open seat selection": "Odpri izbiro sede\u017eev",
    "widget\u0004Previous month": "Prej\u0161nji mesec",
    "widget\u0004Redeem": "Izkoristi",
    "widget\u0004Redeem a voucher": "Izkoristi vav\u010der",
    "widget\u0004Register": "Register",
    "widget\u0004Reserved": "Rezervirano",
    "widget\u0004Resume checkout": "Nadaljujte s checkoutom",
    "widget\u0004See variations": "Poglej vrste",
    "widget\u0004Sold out": "Razprodano",
    "widget\u0004The cart could not be created. Please try again later": "Ko\u0161arice ni bilo mogo\u010de ustvariti. Poskusite ponovno kasneje",
    "widget\u0004The ticket shop could not be loaded.": "Trgovine z vstopnicami ni bilo mogo\u010de nalo\u017eiti.",
    "widget\u0004Voucher code": "Koda vav\u010derja",
    "widget\u0004Waiting list": "\u010cakalni seznam",
    "widget\u0004You currently have an active cart for this event. If you select more products, they will be added to your existing cart.": "Imate aktivno ko\u0161arico za ta dogodek. \u010ce izberete ve\u010d izdelkov, bodo dodani v obstoje\u010do ko\u0161arico.",
    "widget\u0004currently available: %s": "trenutno na voljo: %s",
    "widget\u0004from %(currency)s %(price)s": "od %(currency)s %(price)s",
    "widget\u0004incl. %(rate)s% %(taxname)s": "vsebuje %(rate)s% %(taxname)s",
    "widget\u0004incl. taxes": "vsebuje davek",
    "widget\u0004minimum amount to order: %s": "najmanj\u0161a koli\u010dina za naro\u010dilo: %s",
    "widget\u0004plus %(rate)s% %(taxname)s": "plus %(rate)s% %(taxname)s",
    "widget\u0004plus taxes": "plus davek"
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
    "DATETIME_FORMAT": "j. F Y. H:i",
    "DATETIME_INPUT_FORMATS": [
      "%d.%m.%Y %H:%M:%S",
      "%d.%m.%Y %H:%M:%S.%f",
      "%d.%m.%Y %H:%M",
      "%d.%m.%y %H:%M:%S",
      "%d.%m.%y %H:%M:%S.%f",
      "%d.%m.%y %H:%M",
      "%d-%m-%Y %H:%M:%S",
      "%d-%m-%Y %H:%M:%S.%f",
      "%d-%m-%Y %H:%M",
      "%d. %m. %Y %H:%M:%S",
      "%d. %m. %Y %H:%M:%S.%f",
      "%d. %m. %Y %H:%M",
      "%d. %m. %y %H:%M:%S",
      "%d. %m. %y %H:%M:%S.%f",
      "%d. %m. %y %H:%M",
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%Y-%m-%d"
    ],
    "DATE_FORMAT": "d. F Y",
    "DATE_INPUT_FORMATS": [
      "%d.%m.%Y",
      "%d.%m.%y",
      "%d-%m-%Y",
      "%d. %m. %Y",
      "%d. %m. %y",
      "%Y-%m-%d"
    ],
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": 0,
    "MONTH_DAY_FORMAT": "j. F",
    "NUMBER_GROUPING": 3,
    "SHORT_DATETIME_FORMAT": "j.n.Y. H:i",
    "SHORT_DATE_FORMAT": "j. M. Y",
    "THOUSAND_SEPARATOR": ".",
    "TIME_FORMAT": "H:i",
    "TIME_INPUT_FORMATS": [
      "%H:%M:%S",
      "%H:%M:%S.%f",
      "%H:%M"
    ],
    "YEAR_MONTH_FORMAT": "F Y"
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

