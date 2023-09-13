

'use strict';
{
  const globals = this;
  const django = globals.django || (globals.django = {});

  
  django.pluralidx = function(n) {
    const v = n==1 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2;
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
      "(jedna data wi\u0119cej)",
      "({num} daty wi\u0119cej)",
      "({num} dat wi\u0119cej)"
    ],
    "All": "Zaznacz wszystko",
    "An error has occurred.": "Wyst\u0105pi\u0142 b\u0142\u0105d.",
    "An error of type {code} occurred.": "Wyst\u0105pi\u0142 b\u0142\u0105d typu {code}.",
    "April": "Kwiecie\u0144",
    "August": "Sierpie\u0144",
    "Barcode area": "Miejsce na kod kreskowy",
    "Calculating default price\u2026": "Liczenie domy\u015blnej ceny\u2026",
    "Cart expired": "Koszyk wygas\u0142",
    "Check-in QR": "QR zameldowania",
    "Click to close": "Zamknij",
    "Close message": "Zamkni\u0119cie wiadomo\u015bci",
    "Comment:": "Komentarz:",
    "Confirming your payment \u2026": "Potwierdzanie p\u0142atno\u015bci\u2026",
    "Contacting Stripe \u2026": "Kontaktowanie Stripe\u2026",
    "Contacting your bank \u2026": "\u0141\u0105czenie z bankiem\u2026",
    "Copied!": "Skopiowano!",
    "Count": "Ilo\u015b\u0107",
    "December": "Grudzie\u0144",
    "Do you really want to leave the editor without saving your changes?": "Czy na pewno opu\u015bci\u0107 edytor bez zapisania zmian?",
    "Error while uploading your PDF file, please try again.": "B\u0142\u0105d uploadu pliku PDF, prosimy spr\u00f3bowa\u0107 ponownie.",
    "February": "Luty",
    "Fr": "Pt",
    "Generating messages \u2026": "Generowanie wiadomo\u015bci\u2026",
    "Group of objects": "Grupa obiekt\u00f3w",
    "January": "Stycze\u0144",
    "July": "Lipiec",
    "June": "Czerwiec",
    "March": "Marzec",
    "Marked as paid": "Oznaczono jako zap\u0142acone",
    "May": "Maj",
    "Mo": "Pn",
    "No": "Nie",
    "None": "Odznacz wszystko",
    "November": "Listopad",
    "Object": "Obiekt",
    "October": "Pa\u017adziernik",
    "Others": "Inne",
    "Paid orders": "Zap\u0142acone zam\u00f3wienia",
    "Placed orders": "Z\u0142o\u017cone zam\u00f3wienia",
    "Please enter a quantity for one of the ticket types.": "Prosz\u0119 wybra\u0107 liczb\u0119 dla jednego z typ\u00f3w bilet\u00f3w.",
    "Powered by pretix": "Wygenerowane przez pretix",
    "Press Ctrl-C to copy!": "Wci\u015bnij Ctrl-C \u017ceby skopiowa\u0107!",
    "Sa": "So",
    "Saving failed.": "B\u0142\u0105d zapisu.",
    "September": "Wrzesie\u0144",
    "Su": "Nd",
    "Text object": "Obiekt tekstowy",
    "Th": "Cz",
    "The PDF background file could not be loaded for the following reason:": "B\u0142\u0105d \u0142adowania pliku PDF t\u0142a:",
    "Ticket design": "Projekt biletu",
    "Total": "Razem",
    "Total revenue": "Ca\u0142kowity doch\u00f3d",
    "Tu": "Wt",
    "Unknown error.": "Nieznany b\u0142\u0105d.",
    "Use a different name internally": "U\u017cyj innej nazwy wewn\u0119trznie",
    "We": "\u015ar",
    "We are currently sending your request to the server. If this takes longer than one minute, please check your internet connection and then reload this page and try again.": "Zapytanie jest przesy\u0142ane do serwera. W przypadku czasu oczekiwania d\u0142u\u017cszego ni\u017c minuta prosimy o sprawdzenie \u0142\u0105czno\u015bci z Internetem a nast\u0119pnie o prze\u0142adowanie strony i ponowienie\u00a0pr\u00f3by.",
    "We are processing your request \u2026": "Zapytanie jest przetwarzane\u2026",
    "We currently cannot reach the server, but we keep trying. Last error code: {code}": "B\u0142\u0105d komunikacji z serwerem, aplikacja ponowi pr\u00f3b\u0119. Ostatni kod b\u0142\u0119du: {code}",
    "We currently cannot reach the server. Please try again. Error code: {code}": "B\u0142\u0105d komunikacji z serwerem. Prosimy spr\u00f3bowa\u0107\u00a0ponownie. Kod b\u0142\u0119du: {code}",
    "Yes": "Tak",
    "Your color has bad contrast for text on white background, please choose a darker shade.": "Wybrany kolor ma za s\u0142aby kontrast dla tekstu na bia\u0142ym tle, prosimy wybra\u0107 ciemniejszy odcie\u0144.",
    "Your color has decent contrast and is probably good-enough to read!": "Wybrany kolor ma odpowiedni kontrast i zapewnia wystarczaj\u0105c\u0105 czytelno\u015b\u0107!",
    "Your color has great contrast and is very easy to read!": "Wybrany kolor ma wysoki kontrast i zapewnia doskona\u0142\u0105 czytelno\u015b\u0107!",
    "Your request arrived on the server but we still wait for it to be processed. If this takes longer than two minutes, please contact us or go back in your browser and try again.": "Zapytanie zosta\u0142o dotar\u0142o do serwera ale jest wci\u0105\u017c\u00a0przetwarzane. W przypadku czasu oczekiwania d\u0142u\u017cszego ni\u017c dwie minuty prosimy o kontakt lub o cofni\u0119cie si\u0119 w przegl\u0105darce i ponowienie pr\u00f3by.",
    "widget\u0004Back": "Wstecz",
    "widget\u0004Buy": "Kup",
    "widget\u0004Choose a different date": "Wybierz inn\u0105 dat\u0119",
    "widget\u0004Choose a different event": "Wybierz inne wydarzenie",
    "widget\u0004Close": "Zamkn\u0105\u0107",
    "widget\u0004Close ticket shop": "Zamkni\u0119cie sklepu biletowego",
    "widget\u0004Continue": "Dalej",
    "widget\u0004FREE": "DARMOWE",
    "widget\u0004Next month": "Przysz\u0142y miesi\u0105c",
    "widget\u0004Only available with a voucher": "Dost\u0119pne tylko z voucherem",
    "widget\u0004Open seat selection": "Otw\u00f3rz wyb\u00f3r miejsca",
    "widget\u0004Previous month": "Zesz\u0142y miesi\u0105c",
    "widget\u0004Redeem": "U\u017cyj",
    "widget\u0004Redeem a voucher": "U\u017cyj vouchera",
    "widget\u0004Register": "Rejestracja",
    "widget\u0004Reserved": "Zarezerwowane",
    "widget\u0004Resume checkout": "Powr\u00f3t do kasy",
    "widget\u0004See variations": "Mo\u017cliwe warianty",
    "widget\u0004Sold out": "Wyprzedane",
    "widget\u0004The cart could not be created. Please try again later": "B\u0142\u0105d tworzenia koszyka. Prosimy\u00a0spr\u00f3bowa\u0107\u00a0ponownie p\u00f3\u017aniej",
    "widget\u0004The ticket shop could not be loaded.": "B\u0142\u0105d \u0142\u0105dowania sklepu biletowego.",
    "widget\u0004Voucher code": "Kod vouchera",
    "widget\u0004Waiting list": "Lista oczekiwania",
    "widget\u0004You currently have an active cart for this event. If you select more products, they will be added to your existing cart.": "Istnieje aktywny w\u00f3zek dla tego wydarzenia. Wyb\u00f3r kolejnych produkt\u00f3w spowoduje dodanie ich do istniej\u0105cego w\u00f3zka.",
    "widget\u0004currently available: %s": "obecnie dost\u0119pne: %s",
    "widget\u0004from %(currency)s %(price)s": "od %(currency)s %(price)s",
    "widget\u0004incl. %(rate)s% %(taxname)s": "w tym %(rate)s% %(taxname)s",
    "widget\u0004incl. taxes": "Brutto",
    "widget\u0004minimum amount to order: %s": "minimalna ilo\u015b\u0107 zam\u00f3wienia: %s",
    "widget\u0004plus %(rate)s% %(taxname)s": "plus %(rate)s% %(taxname)s",
    "widget\u0004plus taxes": "netto"
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
    "DATETIME_FORMAT": "j E Y H:i",
    "DATETIME_INPUT_FORMATS": [
      "%d.%m.%Y %H:%M:%S",
      "%d.%m.%Y %H:%M:%S.%f",
      "%d.%m.%Y %H:%M",
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%Y-%m-%d"
    ],
    "DATE_FORMAT": "j E Y",
    "DATE_INPUT_FORMATS": [
      "%d.%m.%Y",
      "%d.%m.%y",
      "%y-%m-%d",
      "%Y-%m-%d"
    ],
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": 1,
    "MONTH_DAY_FORMAT": "j E",
    "NUMBER_GROUPING": 3,
    "SHORT_DATETIME_FORMAT": "d-m-Y  H:i",
    "SHORT_DATE_FORMAT": "d-m-Y",
    "THOUSAND_SEPARATOR": "\u00a0",
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

