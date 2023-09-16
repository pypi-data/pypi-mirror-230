class LongUnits:
    @staticmethod
    def km_to_m(km):
        m = km * 1000
        if km <= 0:
            raise ValueError("NumberError: km can't be <= 0")
        else:
            return m

    @staticmethod
    def m_to_km(m):
        km = m / 1000
        if m <= 0:
            raise ValueError("NumberError: m can't be <= 0")
        else:
            return km

    @staticmethod
    def dm_to_m(dm):
        m = dm / 10
        if dm <= 0:
            raise ValueError("NumberError: dm can't be <= 0")
        else:
            return m

    @staticmethod
    def m_to_dm(m):
        dm = m * 10
        if m <= 0:
            raise ValueError("NumberError: m can't be <= 0")
        else:
            return dm

    @staticmethod
    def mm_to_m(mm):
        m = mm / 1000
        if mm <= 0:
            raise ValueError("NumberError: mm can't be <= 0")
        else:
            return m

    @staticmethod
    def m_to_mm(m):
        mm = m * 1000
        if m <= 0:
            raise ValueError("NumberError: m can't be <= 0")
        else:
            return mm

    @staticmethod
    def um_to_m(um):
        m = um / 1000000
        if um <= 0:
            raise ValueError("NumberError: um can't be <= 0")
        else:
            return m

    @staticmethod
    def m_to_um(m):
        um = m * 1000000
        if m <= 0:
            raise ValueError("NumberError: m can't be <= 0")
        else:
            return um

    @staticmethod
    def nm_to_m(nm):
        m = nm / 1000000000
        if nm <= 0:
            raise ValueError("NumberError: nm can't be <= 0")
        else:
            return m

    @staticmethod
    def m_to_nm(m):
        nm = m * 1000000000
        if m <= 0:
            raise ValueError("NumberError: m can't be <= 0")
        else:
            return nm

    @staticmethod
    def km_to_dm(km):
        dm = km / 0.1
        if km <= 0:
            raise ValueError("NumberError: km can't be <= 0")
        else:
            return dm

    @staticmethod
    def dm_to_km(dm):
        km = dm * 0.1
        if dm <= 0:
            raise ValueError("NumberError: dm can't be <= 0")
        else:
            return km

    @staticmethod
    def km_to_cm(km):
        cm = km * 100000
        if km <= 0:
            raise ValueError("NumberError: km can't be <= 0")
        else:
            return cm

    @staticmethod
    def cm_to_km(cm):
        km = cm / 100000
        if cm <= 0:
            raise ValueError("NumberError: cm can't be <= 0")
        else:
            return km

    @staticmethod
    def km_to_mm(km):
        mm = km * 1000000
        if km <= 0:
            raise ValueError("NumberError: km can't be <= 0")
        else:
            return mm

    @staticmethod
    def mm_to_km(mm):
        km = mm / 1000000
        if mm <= 0:
            raise ValueError("NumberError: mm can't be <= 0")
        else:
            return km

    @staticmethod
    def km_to_um(km):
        um = km * 1000000000
        if km <= 0:
            raise ValueError("NumberError: km can't be <= 0")
        else:
            return um

    @staticmethod
    def um_to_km(um):
        km = um / 1000000000
        if um <= 0:
            raise ValueError("NumberError: um can't be <= 0")
        else:
            return km

    @staticmethod
    def km_to_nm(km):
        nm = km * 1000000000000
        if km <= 0:
            raise ValueError("NumberError: km can't be <= 0")
        else:
            return nm

    @staticmethod
    def nm_to_km(nm):
        km = nm / 1000000000000
        if nm <= 0:
            raise ValueError("NumberError: nm can't be <= 0")
        else:
            return km
