import json
import simpleworkspace.loader as sw
from basetestcase import BaseTestCase
from simpleworkspace.types.byte import ByteUnit, ByteEnum
from simpleworkspace.types.measurement import LengthEnum, LengthUnit, WeightEnum, WeightUnit
from simpleworkspace.types.time import TimeEnum, TimeSpan

class TimeTests(BaseTestCase):
    def test_TimeEnum_HasCorrectSeconds(self):
        self.assertEqual(TimeEnum.NanoSecond.value  * 2, 0.000000002)
        self.assertEqual(TimeEnum.MicroSecond.value * 2, 0.000002)
        self.assertEqual(TimeEnum.MilliSecond.value * 2, 0.002)
        self.assertEqual(TimeEnum.Second.value      * 2, 2)
        self.assertEqual(TimeEnum.Minute.value      * 2, 120)
        self.assertEqual(TimeEnum.Hour.value        * 2, 7200)
        self.assertEqual(TimeEnum.Day.value         * 2, 172800)
        
    def test_TimeSpann_KnownEqualityChecks(self):
        assert TimeSpan(milliSeconds=2000)  == TimeSpan(seconds=2)
        assert TimeSpan(seconds=2)          == TimeSpan(seconds=2)
        assert TimeSpan(minutes=2)          == TimeSpan(seconds=120)
        
        # Test TimeSpan constructor
        assert TimeSpan().InSeconds() == 0
        assert TimeSpan(seconds=30).InSeconds() == 30
        assert TimeSpan(milliSeconds=500).InSeconds() == 0.5
        assert TimeSpan(minutes=1, seconds=30).InSeconds() == 90

        # Test conversion methods
        assert TimeSpan(seconds=60).InMinutes() == 1
        assert TimeSpan(minutes=120).InHours() == 2
        assert TimeSpan(hours=48).InDays() == 2

        t1 = TimeSpan(seconds=86400)
        self.assertEqual(t1.InMilliseconds(), 1000 * 86400)
        self.assertEqual(t1.InSeconds(), 86400)
        self.assertEqual(t1.InMinutes(), 1440)
        self.assertEqual(t1.InHours(), 24)
        self.assertEqual(t1.InDays(), 1)



        t2 = TimeSpan(milliSeconds=2, seconds=3, minutes=4, hours=5,days=6)
        self.assertEqual(t2.Milliseconds,2)
        self.assertEqual(t2.Seconds,3)
        self.assertEqual(t2.Minutes,4)
        self.assertEqual(t2.Hours,5)
        self.assertEqual(t2.Days,6)

        self.assertEqual(round(t2.InMilliseconds(), 6), 536643002)
        self.assertEqual(round(t2.InSeconds(), 6), 536643.002)
        self.assertEqual(round(t2.InMinutes(), 6), 8944.050033)
        self.assertEqual(round(t2.InHours()  , 6), 149.067501)
        self.assertEqual(round(t2.InDays()   , 6), 6.211146)


        #test very close to roundable numbers, the important part is that seconds should stay as 4 and not round to 5
        t = TimeSpan(days=1, seconds=4, milliSeconds=999)
        assert t.Days == 1
        assert t.Seconds == 4
        assert t.Milliseconds == 999

        #any smaller unit than milliseconds can round but should not be taken into account for equality
        assert TimeSpan(milliSeconds=1.1) == TimeSpan(milliSeconds=1.0)
        assert TimeSpan(milliSeconds=1.9) == TimeSpan(milliSeconds=2.0)
        assert TimeSpan(seconds=1.0011) == TimeSpan(seconds=1, milliSeconds=1) 
        assert TimeSpan(seconds=1.0019) == TimeSpan(seconds=1, milliSeconds=2) 

        pass

    def test_TimeSpann_NegativeEqualityChecks(self):
        self.assertNotEqual(TimeSpan(minutes=2),
                            TimeSpan(seconds=2))
        
        self.assertNotEqual(TimeSpan(minutes=2),
                            TimeSpan(minutes=3))
        
    def test_TimeSpann_ArchimetricOperators(self):
        #quick tests
        time_span1 = TimeSpan(seconds=10)
        time_span2 = TimeSpan(seconds=20)

        assert (time_span1 + time_span2).InSeconds() == 30
        assert (time_span2 - time_span1).InSeconds() == 10

        # Test Addition
        ts = TimeSpan(seconds=1)
        ts += TimeSpan(seconds=1)
        self.assertEqual(ts.Seconds, 2)
        self.assertEqual(TimeSpan(seconds=1) + TimeSpan(seconds=1), TimeSpan(seconds=2))

        # Test subtraction
        ts = TimeSpan(seconds=10)
        ts -= TimeSpan(seconds=2)
        self.assertEqual(ts.Seconds, 8)
        self.assertEqual(TimeSpan(seconds=10) - TimeSpan(seconds=2), TimeSpan(seconds=8))

        #reference test add
        ts = TimeSpan(seconds=1)
        ts_ref = ts
        ts += TimeSpan(seconds=1)
        assert ts_ref is ts

        ts = TimeSpan(seconds=1)
        ts2 = TimeSpan(seconds=1)
        ts3 = ts + ts2
        assert ts3 is not ts
        assert ts3 is not ts2

        #reference sub
        ts = TimeSpan(seconds=1)
        ts_ref = ts
        ts -= TimeSpan(seconds=1)
        assert ts_ref is ts

        ts = TimeSpan(seconds=1)
        ts2 = TimeSpan(seconds=1)
        ts3 = ts - ts2
        assert ts3 is not ts
        assert ts3 is not ts2

        #comparison operators
        assert TimeSpan(seconds=2) == TimeSpan(seconds=2)

        assert TimeSpan(seconds=1) < TimeSpan(seconds=2)
        assert not TimeSpan(seconds=2) < TimeSpan(seconds=2)
        assert not TimeSpan(seconds=3) < TimeSpan(seconds=2)

        assert TimeSpan(seconds=1) <= TimeSpan(seconds=2)
        assert TimeSpan(seconds=2) <= TimeSpan(seconds=2)
        assert not TimeSpan(seconds=3) <= TimeSpan(seconds=2)

        assert TimeSpan(seconds=2) > TimeSpan(seconds=1)
        assert not TimeSpan(seconds=1) > TimeSpan(seconds=1)
        assert not TimeSpan(seconds=2) > TimeSpan(seconds=2)

        assert TimeSpan(seconds=1) >= TimeSpan(seconds=1)
        assert TimeSpan(seconds=2) >= TimeSpan(seconds=1)
        assert not TimeSpan(seconds=0) >= TimeSpan(seconds=1)


    def test_TimeSpan_Partition(self):
        # Test case 1
        parts = TimeSpan(minutes=2, seconds=30).Partition()
        self.assertEqual(parts, {
            TimeEnum.MilliSecond: 0.0,
            TimeEnum.Second: 30.0,
            TimeEnum.Minute: 2.0,
            TimeEnum.Hour: 0.0,
            TimeEnum.Day: 0.0
        })

        # Test case 2
        parts = TimeSpan(seconds=90).Partition()
        self.assertEqual(parts, {
            TimeEnum.MilliSecond: 0.0,
            TimeEnum.Second: 30.0,
            TimeEnum.Minute: 1.0,
            TimeEnum.Hour: 0.0,
            TimeEnum.Day: 0.0
        })

        # Test case 3
        parts = TimeSpan(hours=1, seconds=1).Partition()
        self.assertEqual(parts, {
            TimeEnum.MilliSecond: 0.0,
            TimeEnum.Second: 1.0,
            TimeEnum.Minute: 0.0,
            TimeEnum.Hour: 1.0,
            TimeEnum.Day: 0.0
        })


        # Test case 4
        parts = TimeSpan(minutes=1, seconds=2, milliSeconds=100).Partition()
        parts[TimeEnum.MilliSecond] = round(parts[TimeEnum.MilliSecond], 6) # get rid of decimal imperfections
        self.assertEqual(parts, {
            TimeEnum.MilliSecond: 100.0,
            TimeEnum.Second: 2.0,
            TimeEnum.Minute: 1.0,
            TimeEnum.Hour: 0.0,
            TimeEnum.Day: 0.0
        })

        # Test case 5: maxPart
        parts = TimeSpan(days=1).Partition(maxUnit=TimeEnum.Hour)
        self.assertEqual(parts, {
            TimeEnum.MilliSecond: 0.0,
            TimeEnum.Second     : 0.0,
            TimeEnum.Minute     : 0.0,
            TimeEnum.Hour       : 24.0,
        })

        # Test case 5: minPart
        parts = TimeSpan(minutes=2, seconds=30).Partition(minUnit=TimeEnum.Minute)
        self.assertEqual(parts, {
            TimeEnum.Minute     : 2.5,
            TimeEnum.Hour       : 0.0,
            TimeEnum.Day        : 0.0
        })

        # Test case 5: minPart and maxPart
        parts = TimeSpan(hours=1, seconds=1, milliSeconds=100).Partition(minUnit=TimeEnum.Second, maxUnit=TimeEnum.Minute)
        parts[TimeEnum.Second] = round(parts[TimeEnum.Second], 6) # get rid of decimal imperfections
        self.assertEqual(parts, {
            TimeEnum.Second     : 1.1,
            TimeEnum.Minute     : 60.0,
        })

    def test_StrictTypeChecks(self):
        with self.assertRaises(TypeError):
            t1 = TimeSpan(seconds=1)
            t1 += 1
        pass





   
class ByteTests(BaseTestCase):
    def test_ByteUnit_Conversions_KnownEqualityChecks(self):
        # Test conversions from Byte to other units
        self.assertEqual(ByteUnit(1, ByteEnum.Byte).To(ByteEnum.Bit), 
                         ByteUnit(8, ByteEnum.Bit))

        self.assertEqual(ByteUnit(1, ByteEnum.Byte).To(ByteEnum.KiloByte), 
                         ByteUnit(0.001, ByteEnum.KiloByte))
        
        self.assertEqual(ByteUnit(1, ByteEnum.Byte).To(ByteEnum.MegaByte),
                         ByteUnit(0.000001, ByteEnum.MegaByte))
        
        self.assertEqual(ByteUnit(1, ByteEnum.Byte).To(ByteEnum.GigaByte), 
                         ByteUnit(0.000000001, ByteEnum.GigaByte))
        
        self.assertEqual(ByteUnit(1, ByteEnum.Byte).To(ByteEnum.TeraByte), 
                         ByteUnit(0.000000000001, ByteEnum.TeraByte))

        # Test conversions from KiloByte to other units
        self.assertEqual(ByteUnit(1000, ByteEnum.KiloByte).To(ByteEnum.Byte), 
                         ByteUnit(1000000, ByteEnum.Byte))
        
        self.assertEqual(ByteUnit(1000, ByteEnum.KiloByte).To(ByteEnum.MegaByte), 
                         ByteUnit(1, ByteEnum.MegaByte))
        
        self.assertEqual(ByteUnit(1000, ByteEnum.KiloByte).To(ByteEnum.GigaByte), 
                         ByteUnit(0.001, ByteEnum.GigaByte))
        
        self.assertEqual(ByteUnit(1000, ByteEnum.KiloByte).To(ByteEnum.TeraByte), 
                         ByteUnit(0.000001, ByteEnum.TeraByte))

        # Test conversions from MegaByte to other units
        self.assertEqual(ByteUnit(1000, ByteEnum.MegaByte).To(ByteEnum.Byte), 
                         ByteUnit(1000000000, ByteEnum.Byte))
        
        self.assertEqual(ByteUnit(1000, ByteEnum.MegaByte).To(ByteEnum.KiloByte), 
                         ByteUnit(1000000, ByteEnum.KiloByte))
        
        self.assertEqual(ByteUnit(1000, ByteEnum.MegaByte).To(ByteEnum.GigaByte), 
                         ByteUnit(1, ByteEnum.GigaByte))
        
        self.assertEqual(ByteUnit(1000, ByteEnum.MegaByte).To(ByteEnum.TeraByte), 
                         ByteUnit(0.001, ByteEnum.TeraByte))

        # Test conversions from GigaByte to other units
        self.assertEqual(ByteUnit(1000, ByteEnum.GigaByte).To(ByteEnum.Byte), 
                         ByteUnit(1000000000000, ByteEnum.Byte))
        
        self.assertEqual(ByteUnit(1000, ByteEnum.GigaByte).To(ByteEnum.KiloByte), 
                         ByteUnit(1000000000, ByteEnum.KiloByte))
        
        self.assertEqual(ByteUnit(1000, ByteEnum.GigaByte).To(ByteEnum.MegaByte), 
                         ByteUnit(1000000, ByteEnum.MegaByte))
        
        self.assertEqual(ByteUnit(1000, ByteEnum.GigaByte).To(ByteEnum.TeraByte), 
                         ByteUnit(1, ByteEnum.TeraByte))

        # Test conversions from TerraByte to other units
        self.assertEqual(ByteUnit(1000, ByteEnum.TeraByte).To(ByteEnum.Byte), 
                         ByteUnit(1000000000000000, ByteEnum.Byte))
        
        self.assertEqual(ByteUnit(1000, ByteEnum.TeraByte).To(ByteEnum.KiloByte), 
                         ByteUnit(1000000000000, ByteEnum.KiloByte))
        
        self.assertEqual(ByteUnit(1000, ByteEnum.TeraByte).To(ByteEnum.MegaByte), 
                         ByteUnit(1000000000, ByteEnum.MegaByte))
        
        self.assertEqual(ByteUnit(1000, ByteEnum.TeraByte).To(ByteEnum.GigaByte), 
                         ByteUnit(1000000, ByteEnum.GigaByte))


        # Test conversions between all possible units
        self.assertEqual(ByteUnit(1024, ByteEnum.Bit).To(ByteEnum.Byte),
                         ByteUnit(128, ByteEnum.Byte))
        
        self.assertEqual(ByteUnit(1024, ByteEnum.Byte).To(ByteEnum.KiloByte),
                         ByteUnit(1.024, ByteEnum.KiloByte))
        
        self.assertEqual(ByteUnit(1.024, ByteEnum.KiloByte).To(ByteEnum.Byte),
                         ByteUnit(1024, ByteEnum.Byte))
        
        self.assertEqual(ByteUnit(1, ByteEnum.MegaByte).To(ByteEnum.GigaByte),
                         ByteUnit(0.001, ByteEnum.GigaByte))
        
        self.assertEqual(ByteUnit(100, ByteEnum.GigaByte).To(ByteEnum.TeraByte),
                         ByteUnit(0.1, ByteEnum.TeraByte))
        
        self.assertEqual(ByteUnit(2000, ByteEnum.KiloByte).To(ByteEnum.MegaByte),
                        ByteUnit(2, ByteEnum.MegaByte))
        
        self.assertEqual(ByteUnit(2, ByteEnum.MegaByte).To(ByteEnum.KiloByte),
                         ByteUnit(2000, ByteEnum.KiloByte))
        
    def test_ByteUnit_NegativeEqualityChecks(self):
        # Test conversions between all possible units
        self.assertNotEqual(ByteUnit(1024, ByteEnum.Byte).To(ByteEnum.KiloByte),
                         ByteUnit(1024, ByteEnum.KiloByte))
        
        self.assertNotEqual(ByteUnit(1.024, ByteEnum.KiloByte).To(ByteEnum.Byte),
                         ByteUnit(1.024, ByteEnum.Byte))
        
        self.assertNotEqual(ByteUnit(1, ByteEnum.MegaByte).To(ByteEnum.GigaByte),
                         ByteUnit(1, ByteEnum.GigaByte))
        
        self.assertNotEqual(ByteUnit(100, ByteEnum.GigaByte).To(ByteEnum.TeraByte),
                         ByteUnit(100, ByteEnum.TeraByte))
        
        self.assertNotEqual(ByteUnit(2000, ByteEnum.KiloByte).To(ByteEnum.MegaByte),
                        ByteUnit(2000, ByteEnum.MegaByte))
        
        self.assertNotEqual(ByteUnit(2, ByteEnum.MegaByte).To(ByteEnum.KiloByte),
                         ByteUnit(2, ByteEnum.KiloByte))

    def test_ByteUnit_EqualityChecksWithDiffentUnits(self):
        # Test conversions between all possible units
        self.assertEqual(ByteUnit(1024, ByteEnum.Byte),
                         ByteUnit(1.024, ByteEnum.KiloByte))
        
        self.assertEqual(ByteUnit(1.024, ByteEnum.KiloByte),
                         ByteUnit(1024, ByteEnum.Byte))
        
        self.assertEqual(ByteUnit(1, ByteEnum.MegaByte),
                         ByteUnit(0.001, ByteEnum.GigaByte))
        
        self.assertEqual(ByteUnit(100, ByteEnum.GigaByte),
                         ByteUnit(0.1, ByteEnum.TeraByte))
        
        self.assertEqual(ByteUnit(2000, ByteEnum.KiloByte),
                        ByteUnit(2, ByteEnum.MegaByte))
        
        self.assertEqual(ByteUnit(2, ByteEnum.MegaByte),
                         ByteUnit(2000, ByteEnum.KiloByte))
        
    def test_ByteUnit_StrictEqualityCheck(self):
        byteUnit = ByteUnit(5, ByteEnum.MegaByte)
        self.assertEqual(byteUnit.To(ByteEnum.Bit     ).amount, 40000000)
        self.assertEqual(byteUnit.To(ByteEnum.Byte    ).amount, 5000000)
        self.assertEqual(byteUnit.To(ByteEnum.KiloByte).amount, 5000)
        self.assertEqual(byteUnit.To(ByteEnum.MegaByte).amount, 5)
        self.assertEqual(byteUnit.To(ByteEnum.GigaByte).amount, 0.005)
        self.assertEqual(byteUnit.To(ByteEnum.TeraByte).amount, 0.000005)

        # Test conversions between all possible units
        convertedUnit = ByteUnit(8192, ByteEnum.Bit).To(ByteEnum.KiloByte)
        self.assertEqual(convertedUnit.amount, 1.024)
        self.assertEqual(convertedUnit.unit, ByteEnum.KiloByte)

        convertedUnit = ByteUnit(1024, ByteEnum.Byte).To(ByteEnum.KiloByte)
        self.assertEqual(convertedUnit.amount, 1.024)
        self.assertEqual(convertedUnit.unit, ByteEnum.KiloByte)

        convertedUnit = ByteUnit(1.024, ByteEnum.KiloByte).To(ByteEnum.Byte)
        self.assertEqual(convertedUnit.amount, 1024)
        self.assertEqual(convertedUnit.unit, ByteEnum.Byte)

        convertedUnit = ByteUnit(1, ByteEnum.MegaByte).To(ByteEnum.GigaByte)
        self.assertEqual(convertedUnit.amount, 0.001)
        self.assertEqual(convertedUnit.unit, ByteEnum.GigaByte)

        convertedUnit = ByteUnit(100, ByteEnum.GigaByte).To(ByteEnum.TeraByte)
        self.assertEqual(convertedUnit.amount, 0.1)
        self.assertEqual(convertedUnit.unit, ByteEnum.TeraByte)

        convertedUnit = ByteUnit(2000, ByteEnum.KiloByte).To(ByteEnum.MegaByte)
        self.assertEqual(convertedUnit.amount, 2)
        self.assertEqual(convertedUnit.unit, ByteEnum.MegaByte)

        convertedUnit = ByteUnit(2, ByteEnum.MegaByte).To(ByteEnum.KiloByte)
        self.assertEqual(convertedUnit.amount, 2000)
        self.assertEqual(convertedUnit.unit, ByteEnum.KiloByte)
    
    def test_ByteUnit_ArchimetricOperators(self):
        # Test Inplace Addition with float
        byte1 = ByteUnit(1, ByteEnum.KiloByte)
        float_val = 1
        byte1 += float_val
        self.assertEqual(byte1.amount, 2)
        self.assertEqual(byte1.unit, ByteEnum.KiloByte)
        # Test Inplace Addition with another unit
        byte1 = ByteUnit(1, ByteEnum.KiloByte)
        byte2 = ByteUnit(500, ByteEnum.Byte)
        byte1 += byte2
        self.assertEqual(byte1.amount, 1.5 )
        self.assertEqual(byte1.unit, ByteEnum.KiloByte)


        # Test Inplace Multiplication with float
        byte1 = ByteUnit(2, ByteEnum.KiloByte)
        float_val = 2
        byte1 *= float_val
        self.assertEqual(byte1.amount, 4)
        # Test Inplace Multiplication with another unit
        byte1 = ByteUnit(2, ByteEnum.KiloByte)
        byte2 = ByteUnit(2, ByteEnum.KiloByte)
        byte1 *= byte2
        self.assertEqual(byte1.amount, 4 )


        # Test Inplace Division with float
        byte1 = ByteUnit(6, ByteEnum.MegaByte)
        float_val = 3
        byte1 /= float_val
        self.assertEqual(byte1.amount, 2 )
        # Test Inplace Division with another unit
        byte1 = ByteUnit(6, ByteEnum.MegaByte)
        byte2 = ByteUnit(3000, ByteEnum.KiloByte)
        byte1 /= byte2
        self.assertEqual(byte1.amount, 2)


        # Test Inplace Subtraction with float
        byte1 = ByteUnit(3, ByteEnum.KiloByte)
        float_val = 1.0
        byte1 -= float_val
        self.assertEqual(byte1.amount, 2.0 )
        # Test Inplace Subtraction with another unit
        byte1 = ByteUnit(1, ByteEnum.GigaByte)
        byte2 = ByteUnit(500, ByteEnum.MegaByte)
        byte1 -= byte2
        self.assertEqual(byte1.amount, 0.5)

        # Test greater then with another unit
        u1 = ByteUnit(1, ByteEnum.MegaByte)
        u2 = ByteUnit(500, ByteEnum.KiloByte)

        assert u1 > u2
        assert u1 >= u2
        assert u2 < u1
        assert u2 <= u1

        assert u2 >= u2
        assert u2 <= u2


    def test_byteUnit_getparts(self):
        # Test case 1
        parts =  ByteUnit(1.5, ByteEnum.MegaByte).GetParts()
        self.assertEqual(parts, {
            ByteEnum.Bit: 0.0,
            ByteEnum.Byte: 0.0,
            ByteEnum.KiloByte: 500.0,
            ByteEnum.MegaByte: 1.0,
            ByteEnum.GigaByte: 0.0,
            ByteEnum.TeraByte: 0.0,
            ByteEnum.PetaByte: 0.0,
            ByteEnum.ExaByte: 0.0,
        })

        #test case 2, maxpart
        parts =  ByteUnit(1.5, ByteEnum.MegaByte).GetParts(maxPart=ByteEnum.KiloByte)
        self.assertEqual(parts, {
            ByteEnum.Bit: 0.0,
            ByteEnum.Byte: 0.0,
            ByteEnum.KiloByte: 1500.0,
        })

        #test case 3, minpart
        parts =  ByteUnit(1500, ByteEnum.KiloByte).GetParts(minPart=ByteEnum.MegaByte)
        self.assertEqual(parts, {
            ByteEnum.MegaByte: 1.5,
            ByteEnum.GigaByte: 0.0,
            ByteEnum.TeraByte: 0.0,
            ByteEnum.PetaByte: 0.0,
            ByteEnum.ExaByte: 0.0,
        })


        #test case 4, minpart & maxpart
        parts =  ByteUnit(1002.1, ByteEnum.MegaByte).GetParts(minPart=ByteEnum.MegaByte, maxPart=ByteEnum.GigaByte)
        self.assertEqual(parts, {
            ByteEnum.MegaByte: 2.1,
            ByteEnum.GigaByte: 1.0,
        })

class WeightTests(BaseTestCase):
    def test_WeightUnit_Conversions_KnownEqualityChecks(self):
        # Test conversions from Gram to other units
        assert WeightUnit(1, WeightEnum.Gram).To(WeightEnum.Nanogram) \
            .Equals(WeightUnit(1000000000, WeightEnum.Nanogram), decimalPrecision=6)
        
        self.assertEqual(WeightUnit(1, WeightEnum.Gram).To(WeightEnum.Microgram), 
                         WeightUnit(1000000, WeightEnum.Microgram))
        self.assertEqual(WeightUnit(1, WeightEnum.Gram).To(WeightEnum.Milligram), 
                         WeightUnit(1000, WeightEnum.Milligram))
        
        self.assertEqual(WeightUnit(1, WeightEnum.Gram).To(WeightEnum.Kilogram), 
                         WeightUnit(0.001, WeightEnum.Kilogram))
        
        assert WeightUnit(1, WeightEnum.Gram).To(WeightEnum.Pound) \
            .Equals(WeightUnit(0.002204622621, WeightEnum.Pound), decimalPrecision=6)
        
        assert WeightUnit(1, WeightEnum.Gram).To(WeightEnum.Ounce) \
            .Equals(WeightUnit(0.035273961949, WeightEnum.Ounce), decimalPrecision=6)

        # Test conversions from Kilogram to other units
        self.assertEqual(WeightUnit(1000, WeightEnum.Kilogram).To(WeightEnum.Gram), 
                         WeightUnit(1000000, WeightEnum.Gram))

        assert WeightUnit(1000, WeightEnum.Kilogram).To(WeightEnum.Pound) \
            .Equals(WeightUnit(2204.622621848775, WeightEnum.Pound), decimalPrecision=6)
        
        assert WeightUnit(1000, WeightEnum.Kilogram).To(WeightEnum.Ounce) \
            .Equals(WeightUnit(35273.961949580412, WeightEnum.Ounce), decimalPrecision=6)

        # Test conversions from Pound to other units
        self.assertEqual(WeightUnit(1, WeightEnum.Pound).To(WeightEnum.Gram), 
                         WeightUnit(453.59237, WeightEnum.Gram))
        
        self.assertEqual(WeightUnit(1, WeightEnum.Pound).To(WeightEnum.Kilogram), 
                         WeightUnit(0.45359237, WeightEnum.Kilogram))
        
        self.assertEqual(WeightUnit(1, WeightEnum.Pound).To(WeightEnum.Ounce), 
                         WeightUnit(16, WeightEnum.Ounce))

        # Test conversions from Ounce to other units
        self.assertEqual(WeightUnit(1, WeightEnum.Ounce).To(WeightEnum.Gram), 
                         WeightUnit(28.349523125, WeightEnum.Gram))
        
        self.assertEqual(WeightUnit(1, WeightEnum.Ounce).To(WeightEnum.Kilogram), 
                         WeightUnit(0.028349523125, WeightEnum.Kilogram))
        
        self.assertEqual(WeightUnit(1, WeightEnum.Ounce).To(WeightEnum.Pound), 
                         WeightUnit(0.0625, WeightEnum.Pound))

        # Test conversions between all possible units
        self.assertEqual(WeightUnit(1000, WeightEnum.Gram).To(WeightEnum.Kilogram),
                         WeightUnit(1, WeightEnum.Kilogram))
        
        self.assertEqual(WeightUnit(1000, WeightEnum.Kilogram).To(WeightEnum.Gram),
                         WeightUnit(1000000, WeightEnum.Gram))
        
        self.assertEqual(WeightUnit(1, WeightEnum.Pound).To(WeightEnum.Ounce),
                         WeightUnit(16, WeightEnum.Ounce))
        
        self.assertEqual(WeightUnit(16, WeightEnum.Ounce).To(WeightEnum.Pound),
                         WeightUnit(1, WeightEnum.Pound))

    def test_WeightUnit_NegativeEqualityChecks(self):
        # Test conversions between all possible units
        self.assertNotEqual(WeightUnit(1000, WeightEnum.Gram).To(WeightEnum.Kilogram),
                            WeightUnit(1000, WeightEnum.Kilogram))
        
        self.assertNotEqual(WeightUnit(1000, WeightEnum.Kilogram).To(WeightEnum.Gram),
                            WeightUnit(1000, WeightEnum.Gram))
        
        self.assertNotEqual(WeightUnit(1, WeightEnum.Pound).To(WeightEnum.Ounce),
                            WeightUnit(1, WeightEnum.Ounce))
        
        self.assertNotEqual(WeightUnit(16, WeightEnum.Ounce).To(WeightEnum.Pound),
                            WeightUnit(16, WeightEnum.Pound))

    def test_WeightUnit_EqualityChecksWithDiffentUnits(self):
        # Test conversions between all possible units
        self.assertEqual(WeightUnit(1000, WeightEnum.Gram),
                         WeightUnit(1, WeightEnum.Kilogram))
        
        self.assertEqual(WeightUnit(1000, WeightEnum.Kilogram),
                         WeightUnit(1000000, WeightEnum.Gram))
        
        self.assertEqual(WeightUnit(1, WeightEnum.Pound),
                         WeightUnit(16, WeightEnum.Ounce))
        
        self.assertEqual(WeightUnit(16, WeightEnum.Ounce),
                         WeightUnit(1, WeightEnum.Pound))

    def test_WeightUnit_StrictEqualityCheck(self):
        weightUnit = WeightUnit(5, WeightEnum.Kilogram)
        self.assertEqual(weightUnit.To(WeightEnum.Nanogram).amount, 5000000000000.0)
        self.assertEqual(weightUnit.To(WeightEnum.Microgram).amount, 5000000000.0)
        self.assertEqual(weightUnit.To(WeightEnum.Gram).amount, 5 * 1000)
        self.assertEqual(weightUnit.To(WeightEnum.Kilogram).amount, 5)
        self.assertAlmostEqual(weightUnit.To(WeightEnum.Pound).amount, 11.0231, places=4)
        self.assertAlmostEqual(weightUnit.To(WeightEnum.Ounce).amount, 176.3698, places=4)

        # Test conversions between all possible units
        convertedUnit = WeightUnit(1000, WeightEnum.Gram).To(WeightEnum.Kilogram)
        self.assertEqual(convertedUnit.amount, 1)
        self.assertEqual(convertedUnit.unit, WeightEnum.Kilogram)

        convertedUnit = WeightUnit(1000, WeightEnum.Kilogram).To(WeightEnum.Gram)
        self.assertEqual(convertedUnit.amount, 1000000)
        self.assertEqual(convertedUnit.unit, WeightEnum.Gram)

        convertedUnit = WeightUnit(1, WeightEnum.Pound).To(WeightEnum.Ounce)
        self.assertEqual(convertedUnit.amount, 16)
        self.assertEqual(convertedUnit.unit, WeightEnum.Ounce)

        convertedUnit = WeightUnit(16, WeightEnum.Ounce).To(WeightEnum.Pound)
        self.assertEqual(convertedUnit.amount, 1)
        self.assertEqual(convertedUnit.unit, WeightEnum.Pound)

    def test_WeightUnit_ArchimetricOperators(self):
        # Test Inplace Addition with float
        weight1 = WeightUnit(1, WeightEnum.Kilogram)
        float_val = 1
        weight1 += float_val
        self.assertEqual(weight1.amount, 2)
        self.assertEqual(weight1.unit, WeightEnum.Kilogram)
        # Test Inplace Addition with another unit
        weight1 = WeightUnit(1, WeightEnum.Kilogram)
        weight2 = WeightUnit(500, WeightEnum.Gram)
        weight1 += weight2
        self.assertEqual(weight1.amount, 1.5 )
        self.assertEqual(weight1.unit, WeightEnum.Kilogram)


        # Test Inplace Multiplication with float
        weight1 = WeightUnit(2, WeightEnum.Kilogram)
        float_val = 2
        weight1 *= float_val
        self.assertEqual(weight1.amount, 4)
        # Test Inplace Multiplication with another unit
        weight1 = WeightUnit(2, WeightEnum.Kilogram)
        weight2 = WeightUnit(2, WeightEnum.Kilogram)
        weight1 *= weight2
        self.assertEqual(weight1.amount, 4 )


        # Test Inplace Division with float
        weight1 = WeightUnit(6, WeightEnum.Kilogram)
        float_val = 3
        weight1 /= float_val
        self.assertEqual(weight1.amount, 2 )
        # Test Inplace Division with another unit
        weight1 = WeightUnit(6, WeightEnum.Kilogram)
        weight2 = WeightUnit(3, WeightEnum.Kilogram)
        weight1 /= weight2
        self.assertEqual(weight1.amount, 2)


        # Test Inplace Subtraction with float
        weight1 = WeightUnit(3, WeightEnum.Kilogram)
        float_val = 1.0
        weight1 -= float_val
        self.assertEqual(weight1.amount, 2.0 )
        # Test Inplace Subtraction with another unit
        weight1 = WeightUnit(1, WeightEnum.Kilogram)
        weight2 = WeightUnit(500, WeightEnum.Gram)
        weight1 -= weight2
        self.assertEqual(weight1.amount, 0.5)

class LengthTests(BaseTestCase):
    def test_LengthUnit_Conversions_KnownEqualityChecks(self):
        # Test conversions from Millimeter to other units
        self.assertEqual(LengthUnit(1, LengthEnum.Millimeter).To(LengthEnum.Nanometer),
                         LengthUnit(1000000, LengthEnum.Nanometer))
        
        assert LengthUnit(1, LengthEnum.Millimeter).To(LengthEnum.Micrometer) \
                    .Equals(LengthUnit(1000, LengthEnum.Micrometer), decimalPrecision=8)
        
        self.assertEqual(LengthUnit(1, LengthEnum.Millimeter).To(LengthEnum.Centimeter),
                         LengthUnit(0.1, LengthEnum.Centimeter))
        
        self.assertEqual(LengthUnit(1, LengthEnum.Millimeter).To(LengthEnum.Meter),
                         LengthUnit(0.001, LengthEnum.Meter))
        
        assert LengthUnit(1, LengthEnum.Millimeter).To(LengthEnum.Inch) \
                    .Equals(LengthUnit(0.0393701, LengthEnum.Inch), decimalPrecision=7)
        
        assert LengthUnit(1, LengthEnum.Millimeter).To(LengthEnum.Foot) \
                    .Equals(LengthUnit(0.00328084, LengthEnum.Foot), decimalPrecision=7)

        # Test conversions from Centimeter to other units
        self.assertEqual(LengthUnit(100, LengthEnum.Centimeter).To(LengthEnum.Millimeter),
                         LengthUnit(1000, LengthEnum.Millimeter))
        
        self.assertEqual(LengthUnit(100, LengthEnum.Centimeter).To(LengthEnum.Meter),
                         LengthUnit(1, LengthEnum.Meter))
        
        assert LengthUnit(100, LengthEnum.Centimeter).To(LengthEnum.Inch) \
                    .Equals(LengthUnit(39.370078740157, LengthEnum.Inch), decimalPrecision=7)
        
        assert LengthUnit(100, LengthEnum.Centimeter).To(LengthEnum.Foot) \
                    .Equals(LengthUnit(3.2808398950131, LengthEnum.Foot), decimalPrecision=7)

        # Test conversions from Meter to other units
        self.assertEqual(LengthUnit(1, LengthEnum.Meter).To(LengthEnum.Millimeter),
                         LengthUnit(1000, LengthEnum.Millimeter))

        self.assertEqual(LengthUnit(1, LengthEnum.Meter).To(LengthEnum.Centimeter),
                         LengthUnit(100, LengthEnum.Centimeter))

        assert LengthUnit(1, LengthEnum.Meter).To(LengthEnum.Inch) \
                    .Equals(LengthUnit(39.370078740157, LengthEnum.Inch), decimalPrecision=7)

        assert LengthUnit(1, LengthEnum.Meter).To(LengthEnum.Foot) \
                    .Equals(LengthUnit(3.2808398950131, LengthEnum.Foot), decimalPrecision=7)

        # Test conversions from Inch to other units
        self.assertEqual(LengthUnit(1, LengthEnum.Inch).To(LengthEnum.Millimeter),
                         LengthUnit(25.4, LengthEnum.Millimeter))

        self.assertEqual(LengthUnit(1, LengthEnum.Inch).To(LengthEnum.Centimeter),
                         LengthUnit(2.54, LengthEnum.Centimeter))

        self.assertEqual(LengthUnit(1, LengthEnum.Inch).To(LengthEnum.Meter),
                         LengthUnit(0.0254, LengthEnum.Meter))

        assert LengthUnit(1, LengthEnum.Inch).To(LengthEnum.Foot) \
                    .Equals(LengthUnit(0.083333333333, LengthEnum.Foot), decimalPrecision=7)

        # Test conversions from Foot to other units
        self.assertEqual(LengthUnit(1, LengthEnum.Foot).To(LengthEnum.Millimeter),
                         LengthUnit(304.8, LengthEnum.Millimeter))

        self.assertEqual(LengthUnit(1, LengthEnum.Foot).To(LengthEnum.Centimeter),
                         LengthUnit(30.48, LengthEnum.Centimeter))

        self.assertEqual(LengthUnit(1, LengthEnum.Foot).To(LengthEnum.Meter),
                         LengthUnit(0.3048, LengthEnum.Meter))

        assert LengthUnit(1, LengthEnum.Foot).To(LengthEnum.Inch) \
                    .Equals(LengthUnit(12, LengthEnum.Inch), decimalPrecision=7)

    def test_LengthUnit_StrictEqualityCheck(self):
        lengthUnit = LengthUnit(5, LengthEnum.Meter)
        self.assertEqual(lengthUnit.To(LengthEnum.Nanometer).amount, 5000000000)
        self.assertEqual(lengthUnit.To(LengthEnum.Micrometer).amount, 5000000)
        self.assertEqual(lengthUnit.To(LengthEnum.Millimeter).amount, 5000)
        self.assertEqual(lengthUnit.To(LengthEnum.Centimeter).amount, 500)
        self.assertEqual(lengthUnit.To(LengthEnum.Meter).amount, 5)
        self.assertEqual(lengthUnit.To(LengthEnum.Kilometer).amount, 0.005)
        self.assertEqual(lengthUnit.To(LengthEnum.SCANDINAVIAN_Mile).amount, 0.0005)
        self.assertAlmostEqual(lengthUnit.To(LengthEnum.Inch).amount, 196.850393700787)
        self.assertAlmostEqual(lengthUnit.To(LengthEnum.Foot).amount, 16.404199475065)
        self.assertAlmostEqual(lengthUnit.To(LengthEnum.Yard).amount, 5.4680664916885)
        self.assertAlmostEqual(lengthUnit.To(LengthEnum.US_Statute_Mile).amount, 0.003106855961)
        self.assertAlmostEqual(lengthUnit.To(LengthEnum.US_Nautical_Mile).amount, 0.002699784017)

        # Test conversions between all possible units
        convertedUnit = LengthUnit(1000, LengthEnum.Millimeter).To(LengthEnum.Meter)
        self.assertEqual(convertedUnit.amount, 1)
        self.assertEqual(convertedUnit.unit, LengthEnum.Meter)

        convertedUnit = LengthUnit(100, LengthEnum.Centimeter).To(LengthEnum.Meter)
        self.assertEqual(convertedUnit.amount, 1)
        self.assertEqual(convertedUnit.unit, LengthEnum.Meter)

        convertedUnit = LengthUnit(39.370078740157, LengthEnum.Inch).To(LengthEnum.Meter)
        self.assertAlmostEqual(convertedUnit.amount, 1)
        self.assertEqual(convertedUnit.unit, LengthEnum.Meter)

        convertedUnit = LengthUnit(3.2808398950131, LengthEnum.Foot).To(LengthEnum.Meter)
        self.assertAlmostEqual(convertedUnit.amount, 1)
        self.assertEqual(convertedUnit.unit, LengthEnum.Meter)

    def test_LengthUnit_ArithmeticOperators(self):
        # Test Inplace Addition with float
        length1 = LengthUnit(1, LengthEnum.Meter)
        float_val = 1
        length1 += float_val
        self.assertEqual(length1.amount, 2)
        self.assertEqual(length1.unit, LengthEnum.Meter)

        # Test Inplace Addition with another unit
        length1 = LengthUnit(1, LengthEnum.Meter)
        length2 = LengthUnit(100, LengthEnum.Centimeter)
        length1 += length2
        self.assertEqual(length1.amount, 2)
        self.assertEqual(length1.unit, LengthEnum.Meter)

        # Test Inplace Multiplication with float
        length1 = LengthUnit(2, LengthEnum.Meter)
        float_val = 2
        length1 *= float_val
        self.assertEqual(length1.amount, 4)
        self.assertEqual(length1.unit, LengthEnum.Meter)

        # Test Inplace Multiplication with another unit
        length1 = LengthUnit(2, LengthEnum.Meter)
        length2 = LengthUnit(2, LengthEnum.Meter)
        length1 *= length2
        self.assertEqual(length1.amount, 4)

        # Test Inplace Division with float
        length1 = LengthUnit(6, LengthEnum.Meter)
        float_val = 3
        length1 /= float_val
        self.assertEqual(length1.amount, 2)

        # Test Inplace Division with another unit
        length1 = LengthUnit(6, LengthEnum.Meter)
        length2 = LengthUnit(3, LengthEnum.Meter)
        length1 /= length2
        self.assertEqual(length1.amount, 2)

        # Test Inplace Subtraction with float
        length1 = LengthUnit(3, LengthEnum.Meter)
        float_val = 1.0
        length1 -= float_val
        self.assertEqual(length1.amount, 2.0)

        # Test Inplace Subtraction with another unit
        length1 = LengthUnit(1, LengthEnum.Meter)
        length2 = LengthUnit(100, LengthEnum.Centimeter)
        length1 -= length2
        self.assertEqual(length1.amount, 0.0)
